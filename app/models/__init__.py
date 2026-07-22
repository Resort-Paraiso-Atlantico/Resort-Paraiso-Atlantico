# models/__init__.py
from app.models.Base import Base
from app.models.Hospede import Hospede
from app.models.Reserva import Reserva
from app.models.Suite import Suite
from app.models.ReservaSuite import ReservaSuite
from app.models.fornecedor.Fornecedor import Fornecedor
from app.models.pedido import PedidoCompra, PedidoItem
from app.models.produto.Produto import Produto
# conforme for criando novos models, adiciona aqui: