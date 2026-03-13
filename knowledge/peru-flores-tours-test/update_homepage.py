#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from odoo_cli import OdooClient

# IDs found in asset_ids.txt
IDS = {
    'LOGO': 1042,
    'HERO': 1043,
    'MONTANA_7_COLORES': 1044,
    'LAGUNA_HUMANTAY': 1045,
    'SACRED_VALLEY': 1046,
    'CUSCO_CITY': 1047,
    'INCA_TRAIL': 1048,
    'MACHU_PICCHU': 1043 # Using hero image for Machu Picchu tour too or hero
}

CSS = """
<style>
    :root {
        --pf-blue: #060097;
        --pf-purple: #c10fff;
        --pf-dark: #1e293b;
        --pf-text: #67768e;
        --pf-bg-light: #f9f6fe;
        --pf-cta: #ffcd57;
        --pf-teal: #265161;
    }

    #wrap { font-family: 'Inter', sans-serif; color: var(--pf-dark); }
    
    .pf-hero {
        position: relative;
        height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-align: center;
        overflow: hidden;
    }
    
    .pf-hero-video-bg {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100vw;
        height: 100vh;
        transform: translate(-50%, -50%);
        z-index: 0;
        pointer-events: none;
    }
    
    @media (min-aspect-ratio: 16/9) {
      .pf-hero-video-bg { height: 56.25vw; }
    }
    @media (max-aspect-ratio: 16/9) {
      .pf-hero-video-bg { width: 177.78vh; }
    }

    .pf-hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.4);
        z-index: 1;
    }
    
    .pf-hero .container {
        position: relative;
        z-index: 2;
    }
    
    .pf-hero h1 { font-size: 4rem; font-weight: 800; text-transform: uppercase; }
    
    .pf-section-title { text-align: center; margin-bottom: 3rem; }
    .pf-section-title h2 { font-size: 2.5rem; font-weight: 700; color: var(--pf-dark); }
    
    .pf-tour-card {
        border: none;
        border-radius: 15px;
        overflow: hidden;
        transition: transform 0.3s;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .pf-tour-card:hover { transform: translateY(-10px); }
    .pf-card-img { height: 250px; object-fit: cover; }
    .pf-card-body { padding: 1.5rem; background: white; }
    .pf-card-tag { 
        background: var(--pf-teal); 
        color: white; 
        padding: 0.3rem 0.8rem; 
        border-radius: 5px; 
        font-size: 0.8rem; 
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .pf-dest-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 1rem;
        border: 4px solid white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .pf-footer {
        background: var(--pf-teal);
        color: white;
        padding: 4rem 0 2rem;
    }
    .pf-footer a { color: rgba(255,255,255,0.8); text-decoration: none; }
    .pf-footer a:hover { color: white; }
</style>
"""

HOMEPAGE_XML = f"""
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        {CSS}
        <div id="wrap">
            <!-- Hero Section -->
            <section class="pf-hero">
                <!-- YouTube iFrame Background -->
                <iframe class="pf-hero-video-bg" 
                        src="https://www.youtube.com/embed/wAsyrcH6WYs?autoplay=1&amp;mute=1&amp;loop=1&amp;playlist=wAsyrcH6WYs&amp;controls=0&amp;showinfo=0&amp;autohide=1&amp;modestbranding=1" 
                        frameborder="0" 
                        allow="autoplay; muted; fullscreen" 
                        title="YouTube video player">
                </iframe>
                
                <div class="pf-hero-overlay"></div>
                
                <div class="container">
                    <p class="mb-2" style="font-size: 1.2rem;">Encuentra tu próximo</p>
                    <h1 class="display-1">Aventura ahora</h1>
                </div>
            </section>

            <!-- About Section -->
            <section class="py-5" style="background: white;">
                <div class="container py-5">
                    <div class="row align-items-center">
                        <div class="col-lg-6">
                            <div class="position-relative" style="height: 500px;">
                                <img src="/web/image/{IDS['MONTANA_7_COLORES']}" class="img-fluid rounded shadow position-absolute" style="width: 70%; top: 0; left: 0; z-index: 2; border: 10px solid white;"/>
                                <img src="/web/image/{IDS['LAGUNA_HUMANTAY']}" class="img-fluid rounded shadow position-absolute" style="width: 70%; bottom: 0; right: 0; z-index: 1; border: 10px solid white;"/>
                            </div>
                        </div>
                        <div class="col-lg-6 ps-lg-5">
                            <p class="text-uppercase tracking-widest" style="color: var(--pf-text);">Encuentra tu próximo</p>
                            <h2 class="display-4 fw-bold mb-4">Aventura ahora</h2>
                            <p class="lead text-muted mb-4">
                                Bienvenido a Perú Flores Tours, donde cada viaje se convierte en una historia romántica cautivante entre el viajero y el destino.
                            </p>
                            <p class="text-muted">
                                En Peru Flores Tours, no solo vendemos destinos; creamos experiencias entrelazadas con amor y felicidad. Nos dedicamos a transformar sueños en realidad. Cada viaje es una oportunidad para alcanzar metas y construir memorias indelebiles.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Why Us -->
            <section class="py-5 bg-light">
                <div class="container text-center py-4">
                    <p class="text-muted mb-1 small">¿Por qué viajar con?</p>
                    <h2 class="fw-bold mb-4">Tours de flores en Perú</h2>
                    <div class="row justify-content-center">
                        <div class="col-lg-8">
                            <p class="text-muted px-4" style="line-height: 1.8;">
                                Viajar con Peru Flores Tours significa más que visitar destinos; es un encuentro con la propia esencia de la aventura y elegancia. Cuidamos cada detalle para hacer de su viaje una narrativa personalizada de amor, alegría y descubrimiento.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Popular Tours -->
            <section class="py-5">
                <div class="container py-5">
                    <div class="pf-section-title">
                        <p class="text-muted mb-0">Las excursiones</p>
                        <h2>Los más populares</h2>
                    </div>
                    <div class="row">
                        <!-- Machu Picchu -->
                        <div class="col-md-4">
                            <div class="pf-tour-card">
                                <img src="/web/image/{IDS['MACHU_PICCHU']}" class="pf-card-img w-100"/>
                                <div class="pf-card-body">
                                    <h5 class="fw-bold">Machu Picchu</h5>
                                    <div class="d-flex justify-content-between align-items-center mt-3">
                                        <span class="text-muted small"><i class="fa fa-clock-o"></i> Full Day</span>
                                        <a href="#" class="btn btn-sm" style="background: var(--pf-teal); color: white;">Explorar <i class="fa fa-chevron-right ms-1" style="font-size: 0.7rem;"></i></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- Rainbow Mountain -->
                        <div class="col-md-4">
                            <div class="pf-tour-card">
                                <img src="/web/image/{IDS['MONTANA_7_COLORES']}" class="pf-card-img w-100"/>
                                <div class="pf-card-body">
                                    <h5 class="fw-bold">Montaña 7 Colores</h5>
                                    <div class="d-flex justify-content-between align-items-center mt-3">
                                        <span class="text-muted small"><i class="fa fa-clock-o"></i> Full Day</span>
                                        <a href="#" class="btn btn-sm" style="background: var(--pf-teal); color: white;">Explorar <i class="fa fa-chevron-right ms-1" style="font-size: 0.7rem;"></i></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- Humantay -->
                        <div class="col-md-4">
                            <div class="pf-tour-card">
                                <img src="/web/image/{IDS['LAGUNA_HUMANTAY']}" class="pf-card-img w-100"/>
                                <div class="pf-card-body">
                                    <h5 class="fw-bold">Laguna Humantay</h5>
                                    <div class="d-flex justify-content-between align-items-center mt-3">
                                        <span class="text-muted small"><i class="fa fa-clock-o"></i> Full Day</span>
                                        <a href="#" class="btn btn-sm" style="background: var(--pf-teal); color: white;">Explorar <i class="fa fa-chevron-right ms-1" style="font-size: 0.7rem;"></i></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Destinations Circular -->
            <section class="py-5 bg-light">
                <div class="container text-center py-5">
                    <p class="text-muted mb-0">Nuestros destinos</p>
                    <h2 class="fw-bold mb-5 display-5">En Cusco</h2>
                    <div class="row">
                        <div class="col-3 mb-4">
                            <img src="/web/image/{IDS['SACRED_VALLEY']}" class="pf-dest-circle"/>
                            <h6 class="fw-bold">Ancasmarca</h6>
                        </div>
                        <div class="col-3 mb-4">
                            <img src="/web/image/{IDS['CUSCO_CITY']}" class="pf-dest-circle"/>
                            <h6 class="fw-bold">Lares</h6>
                        </div>
                        <div class="col-3 mb-4">
                            <img src="/web/image/{IDS['INCA_TRAIL']}" class="pf-dest-circle"/>
                            <h6 class="fw-bold">Willoq</h6>
                        </div>
                        <div class="col-3 mb-4">
                            <img src="/web/image/{IDS['HERO']}" class="pf-dest-circle"/>
                            <h6 class="fw-bold">Poc Poc</h6>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Footer -->
            <footer class="pf-footer">
                <div class="container">
                    <div class="row">
                        <div class="col-md-4 mb-4">
                            <img src="/web/image/{IDS['LOGO']}" style="height: 100px; filter: brightness(0) invert(1);" class="mb-4"/>
                            <p>Cusco, Perú</p>
                            <p>peruflorestours@hotmail.com</p>
                            <p>+51 974 332 732</p>
                        </div>
                        <div class="col-md-4 mb-4">
                            <h5 class="fw-bold mb-4">Enlaces rápidos</h5>
                            <ul class="list-unstyled">
                                <li class="mb-2"><a href="#">Paquetes</a></li>
                                <li class="mb-2"><a href="#">Sobre nosotros</a></li>
                                <li class="mb-2"><a href="#">Términos y condiciones</a></li>
                                <li class="mb-2"><a href="#">Política de privacidad</a></li>
                            </ul>
                        </div>
                        <div class="col-md-4 mb-4">
                            <h5 class="fw-bold mb-4">La empresa y el contacto</h5>
                            <p>Dedicados a crear experiencias únicas y memorias indelébles en el corazón de los Andes.</p>
                        </div>
                    </div>
                    <hr class="mt-4 mb-4" style="border-color: rgba(255,255,255,0.1);"/>
                    <div class="text-center small">
                        Peru Flores Tours © 2024. Todos los derechos reservados. Desarrollado por MiComercio
                    </div>
                </div>
            </footer>
        </div>
    </t>
</t>
"""

def main():
    try:
        client = OdooClient()
        client.connect()
        
        homepage_view_id = 2096
        
        print(f"Updating Homepage View (ID: {homepage_view_id})...")
        client.write('ir.ui.view', [homepage_view_id], {
            'arch_db': HOMEPAGE_XML
        })
        print("✅ Homepage view updated successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
