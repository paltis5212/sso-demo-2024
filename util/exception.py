"""
這裡只定義基礎的 Exception，需要其他 Exception 可以在自己的 APP 定義。
code 422 已經被 Flask OpenAPI3 佔據，不建議使用。
"""

from typing import Any

from werkzeug.exceptions import HTTPException

from util.schema import ErrorResponse


class BaseAPIException(HTTPException):
    code = 500
    message = "Something went wrong."
    response_dict = {}

    def __init__(
        self,
        code: int = None,
        success: bool = None,
        message: str = None,
        data: Any = None,
    ):
        if code:
            self.code = code
        if message:
            self.message = message

        # 預設 message 放入
        self.response_dict["message"] = self.message
        # message 以外，ErrorResponse 有的參數放入
        self.response_dict.update(
            {
                k: v
                for k, v in locals().items()
                if v
                and k in ["success", "data"]
            }
        )

        super(BaseAPIException, self).__init__(self.message, None)

    def get_body(self, *args, **kwargs):
        return ErrorResponse(**self.response_dict).model_dump_json()

    def get_headers(self, *args, **kwargs):
        return [("Content-Type", "application/json")]


class InternalServerErrorException(BaseAPIException):
    code = 500


class BadRequestException(BaseAPIException):
    code = 400

    def get_body(self, *args, **kwargs):
        return (
            ErrorResponse(message="Invalid input.")
            .model_copy(update=self.response_dict, deep=True)
            .model_dump_json()
        )
