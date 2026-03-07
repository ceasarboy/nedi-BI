"""
图表导出API
支持PNG、PDF、SVG格式导出
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, FileResponse
from typing import Optional
import os
from pathlib import Path

from src.core.config import CONFIG_DIR

router = APIRouter(prefix="/api/chart-export", tags=["chart-export"])

CHARTS_DIR = CONFIG_DIR / "charts"


@router.get("/{chart_filename}/png")
async def export_png(chart_filename: str):
    """导出PNG格式"""
    if not chart_filename.endswith('.png'):
        chart_filename += '.png'
    
    chart_path = CHARTS_DIR / chart_filename
    
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="图表不存在")
    
    return FileResponse(
        path=str(chart_path),
        media_type="image/png",
        filename=chart_filename
    )


@router.get("/{chart_filename}/svg")
async def export_svg(chart_filename: str):
    """导出SVG格式（从PNG转换）"""
    import subprocess
    import tempfile
    
    if not chart_filename.endswith('.png'):
        chart_filename += '.png'
    
    chart_path = CHARTS_DIR / chart_filename
    
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="图表不存在")
    
    svg_filename = chart_filename.replace('.png', '.svg')
    svg_path = CHARTS_DIR / svg_filename
    
    if svg_path.exists():
        return FileResponse(
            path=str(svg_path),
            media_type="image/svg+xml",
            filename=svg_filename
        )
    
    try:
        from PIL import Image
        import io
        
        img = Image.open(chart_path)
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{img.width}" height="{img.height}" viewBox="0 0 {img.width} {img.height}">
  <image width="{img.width}" height="{img.height}" xlink:href="{chart_filename}"/>
</svg>'''
        
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return FileResponse(
            path=str(svg_path),
            media_type="image/svg+xml",
            filename=svg_filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG转换失败: {str(e)}")


@router.get("/{chart_filename}/pdf")
async def export_pdf(chart_filename: str):
    """导出PDF格式"""
    if not chart_filename.endswith('.png'):
        chart_filename += '.png'
    
    chart_path = CHARTS_DIR / chart_filename
    
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="图表不存在")
    
    pdf_filename = chart_filename.replace('.png', '.pdf')
    pdf_path = CHARTS_DIR / pdf_filename
    
    if pdf_path.exists():
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_filename
        )
    
    try:
        from PIL import Image
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        
        img = Image.open(chart_path)
        
        if img.width > img.height:
            page_width, page_height = landscape(A4)
        else:
            page_width, page_height = A4
        
        scale = min(
            (page_width - 100) / img.width,
            (page_height - 100) / img.height
        )
        
        new_width = img.width * scale
        new_height = img.height * scale
        
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        
        c = canvas.Canvas(str(pdf_path), pagesize=(page_width, page_height))
        c.drawImage(ImageReader(img), x, y, new_width, new_height)
        c.save()
        
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_filename
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF导出需要安装reportlab库")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")


@router.get("/{chart_filename}/download")
async def download_chart(chart_filename: str, format: str = "png"):
    """下载图表，支持指定格式"""
    format = format.lower()
    
    if format not in ["png", "pdf", "svg"]:
        raise HTTPException(status_code=400, detail="不支持的格式，请使用 png、pdf 或 svg")
    
    if format == "png":
        return await export_png(chart_filename)
    elif format == "svg":
        return await export_svg(chart_filename)
    elif format == "pdf":
        return await export_pdf(chart_filename)
