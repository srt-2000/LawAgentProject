from app.dao.base_dao import BaseDAO
from app.models.models import Message


class MessageDAO(BaseDAO[Message]):

    model = Message