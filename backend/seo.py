# -*- coding: utf-8 -*-
from flask import Blueprint, Response, request, url_for, current_app
from datetime import datetime

seo_bp = Blueprint("seo", __name__)


@seo_bp.route("/robots.txt")
def robots():
    base = request.url_root.rstrip("/")
    body = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@seo_bp.route("/sitemap.xml")
def sitemap():
    views = ["index", "conteudos_page", "page_privacidade", "page_termos"]
    urls = []
    for name in views:
        if name in current_app.view_functions:
            try:
                u = url_for(name, _external=True)
                if u:
                    urls.append(u)
            except Exception:
                pass
    now = datetime.utcnow().strftime("%Y-%m-%d")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f"<url><loc>{u}</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>")
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")
