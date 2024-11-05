from backend.modules.query_controllers.basic.controller import BasicRAGQueryController
from backend.modules.query_controllers.multimodal.controller import (
    MultiModalRAGQueryController,
)
from backend.modules.query_controllers.query_controller import register_query_controller

register_query_controller("multimodal", MultiModalRAGQueryController)
register_query_controller("basic-rag", BasicRAGQueryController)
