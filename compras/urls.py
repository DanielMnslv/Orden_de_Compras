from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registrar-nuevo-compra/", views.registrar_compras, name="registrar_compras"),
    path("lista-de-compras/", views.listar_compras, name="listar_compras"),
    path(
        "detalles-del-compra/<str:id>/",
        views.detalles_compras,
        name="detalles_compras",
    ),
    path(
        "formulario-para-actualizar-compra/<str:id>/",
        views.view_form_update_compra,
        name="view_form_update_compra",
    ),
    path(
        "actualizar-compra/<str:id>/",
        views.actualizar_compra,
        name="actualizar_compra",
    ),
    path("eliminar-compra/", views.eliminar_compra, name="eliminar_compra"),
    path("descargar-informe-compras", views.informe_compra, name="informe_compra"),
    path(
        "formulario-para-la-carga-masiva-de-compras",
        views.view_form_carga_masiva,
        name="view_form_carga_masiva",
    ),
    path("subir-data-xlsx", views.cargar_archivo, name="cargar_archivo"),
]
