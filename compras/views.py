from django.shortcuts import render, redirect
import os
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib import messages  # Para usar mensajes flash
from django.core.exceptions import ObjectDoesNotExist

# Para el informe (Reporte)
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

import json

import logging

from django.http import HttpResponse, JsonResponse

from django.shortcuts import get_object_or_404
from .models import Compra  # Importando el modelo de Compra
from django.core.paginator import Paginator


def inicio(request):
    opciones_edad = [(str(edad), str(edad)) for edad in range(1, 1000)]
    data = {
        "opciones_edad": opciones_edad,
    }
    return render(request, "compras/form_compra.html", data)


def listar_compras(request):
    compras = Compra.objects.all()

    # Configurar la paginación
    paginator = Paginator(compras, 4)  # Por ejemplo, 10 compras por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    data = {
        "compras": page_obj,
    }
    return render(request, "compras/lista_compras.html", data)


def view_form_carga_masiva(request):
    return render(request, "compras/form_carga_masiva.html")


def detalles_compras(request, id):
    try:
        compra = Compra.objects.get(id=id)
        data = {"compra": compra}
        return render(request, "compras/detalles.html", data)
    except Compra.DoesNotExist:
        error_message = f"no existe ningún registro para la busqueda id: {id}"
        return render(
            request, "compras/lista_compras.html", {"error_message": error_message}
        )


def registrar_compras(request):
    if request.method == "POST":
        descripcion = request.POST.get("descripcion")
        codigo_cotizacion = request.POST.get("codigo_cotizacion")
        precio = request.POST.get("precio")
        cantidad = request.POST.get("cantidad")
        empresa = request.POST.get("empresa")
        destino = request.POST.get("destino")
        tiempo_entrega = request.POST.get("tiempo_entrega")
        observaciones = request.POST.get("observaciones")

        # Obtén la imagen del formulario
        foto_producto = request.FILES.get("foto_producto")

        if foto_producto:
            foto_producto = generate_unique_filename(foto_producto)

        # Procesa los datos y guarda en la base de datos
        compra = Compra(
            descripcion=descripcion,
            codigo_cotizacion=codigo_cotizacion,
            precio=precio,
            cantidad=cantidad,
            empresa=empresa,
            destino=destino,
            tiempo_entrega=tiempo_entrega,
            observaciones=observaciones,
            foto_producto=foto_producto,
        )
        compra.save()

        messages.success(
            request,
            f"La compra para {empresa} se registró correctamente 😉",
        )
        # Redirige a la URL con nombre 'listar_compras' definida en urls.py
        return redirect("listar_compras")

    # Si no se ha enviado el formulario, simplemente renderiza la plantilla para el formulario
    return redirect("inicio")


def view_form_update_compra(request, id):
    error_message = f"La Compra con id: {id} no existe."
    return render(
        request, "compras/lista_compras.html", {"error_message": error_message}
    )


def actualizar_compra(request, id):
    try:
        if request.method == "POST":
            # Obtén la compra existente
            compra = Compra.objects.get(id=id)

            compra.descripcion = request.POST.get("descripcion")
            compra.codigo_cotizacion = request.POST.get("codigo_cotizacion")
            compra.precio = request.POST.get("precio")
            compra.cantidad = int(request.POST.get("cantidad"))
            compra.empresa = request.POST.get("empresa")
            compra.destino = request.POST.get("destino")
            compra.tiempo_entrega = request.POST.get("tiempo_entrega")
            compra.observaciones = request.POST.get("observaciones")

            if "foto_producto" in request.FILES:
                # Actualiza la imagen solo si se proporciona en la solicitud
                compra.foto_producto = generate_unique_filename(
                    request.FILES["foto_producto"]
                )

            compra.save()
        return redirect("listar_compras")
    except ObjectDoesNotExist:
        error_message = f"La compra con id: {id} no se actualizó."
        return render(
            request, "compras/lista_compras.html", {"error_message": error_message}
        )


def informe_compra(request):
    try:
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="informe_compra.pdf"'

        # Crear un objeto PDF con orientación horizontal
        doc = SimpleDocTemplate(response, pagesize=landscape(letter))

        styles = getSampleStyleSheet()
        style_heading = styles["Heading1"]
        style_body = styles["BodyText"]

        # Datos de compras desde la base de datos
        datos = Compra.objects.all()

        if not datos.exists():
            return HttpResponse(
                "No hay datos de compras disponibles para generar el informe."
            )

        # Contenido del PDF (Tabla de compras)
        contenido = []
        encabezados = (
            "Descripción",
            "Código de Cotización",
            "Precio",
            "Cantidad",
            "Empresa",
            "Destino",
            "Tiempo de Entrega",
            "Observaciones",
            "Fecha de Registro",
        )
        contenido.append(encabezados)

        for compra in datos:
            contenido.append(
                (
                    compra.descripcion,
                    compra.codigo_cotizacion,
                    compra.precio,
                    compra.cantidad,
                    compra.empresa,
                    compra.destino,
                    compra.tiempo_entrega,
                    compra.observaciones,
                    compra.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),  # Convertir la fecha a una cadena
                )
            )

        # Crear la tabla para el contenido
        tabla = Table(contenido)
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        # Generar el contenido del PDF
        contenido_pdf = []
        contenido_pdf.append(Paragraph("Informe de Compras", style_heading))
        contenido_pdf.append(
            Paragraph(
                "Este es un informe generado automáticamente con los datos de Compras.",
                style_body,
            )
        )
        contenido_pdf.append(tabla)

        # Construir el PDF
        doc.build(contenido_pdf)

        return response

    except Exception as e:
        logging.error(f"Error al generar el informe PDF: {str(e)}")
        return HttpResponse(f"Error al generar el informe PDF: {str(e)}")


def eliminar_compra(request):
    if request.method == "POST":
        id_compra = json.loads(request.body)["idCompra"]
        # Busca la compra por su ID
        compra = get_object_or_404(Compra, id=id_compra)
        # Realiza la eliminación de la compra
        compra.delete()
        return JsonResponse({"resultado": 1})
    return JsonResponse({"resultado": 1})


def cargar_archivo(request):
    try:
        if request.method == "POST":
            archivo_xlsx = request.FILES["archivo_xlsx"]
            if archivo_xlsx.name.endswith(".xlsx"):
                df = pd.read_excel(archivo_xlsx, header=3)

                for _, row in df.iterrows():
                    descripcion = row["descripcion"]
                    codigo_cotizacion = row["codigo_cotizacion"]
                    precio = row["precio"]
                    cantidad = row["cantidad"]
                    empresa = row["empresa"]
                    destino = row["destino"]
                    tiempo_entrega = row["tiempo_entrega"]
                    observaciones = row["observaciones"]

                    compra, creado = Compra.objects.update_or_create(
                        cantidad=cantidad,
                        defaults={
                            "descripcion": descripcion,
                            "codigo_cotizacion": codigo_cotizacion,
                            "precio": precio,
                            "cantidad": cantidad,
                            "empresa": empresa,
                            "destino": destino,
                            "tiempo_entrega": tiempo_entrega,
                            "observaciones": observaciones,
                            "foto_producto": "",
                        },
                    )

                return JsonResponse(
                    {
                        "status_server": "success",
                        "message": "Los datos se importaron correctamente.",
                    }
                )
            else:
                return JsonResponse(
                    {
                        "status_server": "error",
                        "message": "El archivo debe ser un archivo de Excel válido.",
                    }
                )
        else:
            return JsonResponse(
                {"status_server": "error", "message": "Método HTTP no válido."}
            )

    except Exception as e:
        logging.error("Error al cargar el archivo: %s", str(e))
        return JsonResponse(
            {
                "status_server": "error",
                "message": f"Error al cargar el archivo: {str(e)}",
            }
        )


# Genera un nombre único para el archivo utilizando UUID y conserva la extensión.
def generate_unique_filename(file):
    extension = os.path.splitext(file.name)[1]
    unique_name = f"{uuid.uuid4()}{extension}"
    return SimpleUploadedFile(unique_name, file.read())
