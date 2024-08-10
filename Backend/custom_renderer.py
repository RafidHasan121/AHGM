import contextlib

from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # separate data from response
        message = errors = links = count = total_pages = None
        if data is not None:
            message = (
                data.pop("detail")
                if "detail" in data
                else (data.pop("message") if "message" in data else "")
            )
            errors = data.pop("errors") if "errors" in data else None
            data = data.pop("data") if "data" in data else data

            # for pagination class separate data
            links = data.pop("links") if "links" in data else {}
            count = data.pop("count") if "count" in data else 0
            total_pages = data.pop("total_pages") if "total_pages" in data else 0
            data = data.pop("results") if "results" in data else data

        stats_code = renderer_context["response"].status_code
        status = "success" if 199 < stats_code < 299 else "failure"

        # modify error message
        error_msg = ""
        # if errors:
        #     try:
        #         """to avoid any kind of exception during parsing error log exception used"""
        #         error_log = errors[0].split(":")
        #
        #         error_msg = f"{error_log[1].strip().lower().replace('this', error_log[0]).capitalize()}"
        #     except Exception:
        #         error_msg = errors[0].split(":")[1].strip().capitalize()
        errors = data if status == "failure" else {}
        response = data if status == "success" else []
        response_data = {
            "message": error_msg if errors else message,
            "errors": errors,
            "status": status,
            "status_code": stats_code,
            "links": links,
            "count": count,
            "total_pages": total_pages,
            "data": response or [],
        }

        with contextlib.suppress(Exception):
            getattr(
                renderer_context.get("view").get_serializer().Meta,
                "resource_name",
                "objects",
            )

        return super(CustomJSONRenderer, self).render(
            response_data, accepted_media_type, renderer_context
        )


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        if message := response.data.get("detail"):
            response.data = {
                "data": [],
                "message": message,
                "error": [message],
                "success": "failure",
            }

        else:
            try:
                errors = [
                    f'{field} : {" ".join(value)}'
                    for field, value in response.data.items()
                ]
            except AttributeError:
                errors = [
                    f'{field} : {" ".join(str(value))}'
                    for field, value in response.data.items()
                ]

            response.data = {
                "data": [],
                "message": "Validation Error",
                "errors": errors,
                "status": "failure",
            }
    return response
