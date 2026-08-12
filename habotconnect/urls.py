from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from django.shortcuts import redirect

def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HabotConnect - LSA Booking Platform</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f0f4f8;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                max-width: 1100px;
                width: 100%;
            }

            .card {
                background: #ffffff;
                border-radius: 16px;
                padding: 50px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
                border: 1px solid #e8ecf0;
            }

            /* Header */
            .header {
                text-align: center;
                margin-bottom: 40px;
            }

            .logo-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 72px;
                height: 72px;
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                border-radius: 18px;
                font-size: 32px;
                margin-bottom: 16px;
                color: white;
            }

            .header h1 {
                font-size: 36px;
                font-weight: 700;
                color: #1a202c;
                letter-spacing: -0.5px;
            }

            .header h1 span {
                background: linear-gradient(135deg, #4f46e5, #7c3aed);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .header .subtitle {
                font-size: 16px;
                color: #718096;
                margin-top: 8px;
            }

            /* Badges */
            .badge-container {
                display: flex;
                justify-content: center;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 20px;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 16px;
                border-radius: 100px;
                font-size: 12px;
                font-weight: 500;
                background: #f7fafc;
                color: #2d3748;
                border: 1px solid #e2e8f0;
            }

            .badge .dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #48bb78;
                display: inline-block;
            }

            .badge i {
                font-size: 12px;
            }

            /* Stats */
            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 35px;
            }

            .stat-card {
                text-align: center;
                padding: 16px;
                background: #f7fafc;
                border-radius: 12px;
                border: 1px solid #edf2f7;
            }

            .stat-card .number {
                font-size: 24px;
                font-weight: 700;
                color: #1a202c;
                display: block;
            }

            .stat-card .number i {
                color: #4f46e5;
                font-size: 20px;
            }

            .stat-card .label {
                font-size: 13px;
                color: #718096;
                margin-top: 4px;
            }

            /* Section Title */
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #1a202c;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .section-title i {
                color: #4f46e5;
            }

            /* Endpoints Grid */
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 10px;
                margin-bottom: 30px;
            }

            .item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 16px;
                background: #f7fafc;
                border-radius: 10px;
                text-decoration: none;
                color: #2d3748;
                font-weight: 500;
                transition: all 0.2s;
                border: 1px solid #edf2f7;
                font-size: 14px;
            }

            .item:hover {
                background: #edf2f7;
                border-color: #4f46e5;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
            }

            .item .icon {
                font-size: 18px;
                flex-shrink: 0;
            }

            .item .name {
                flex: 1;
            }

            .item .method {
                font-size: 9px;
                font-weight: 600;
                padding: 2px 10px;
                border-radius: 100px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }

            .method-get { background: #c6f6d5; color: #276749; }
            .method-post { background: #bee3f8; color: #2a69ac; }
            .method-put { background: #fefcbf; color: #975a16; }
            .method-delete { background: #fed7d7; color: #9b2c2c; }

            .item-special {
                background: #ebf8ff;
                border-color: #90cdf4;
            }

            .item-special:hover {
                background: #bee3f8;
            }

            .item-danger {
                background: #fff5f5;
                border-color: #feb2b2;
            }

            .item-danger:hover {
                background: #fed7d7;
            }

            /* Footer */
            .footer {
                text-align: center;
                padding-top: 25px;
                border-top: 1px solid #edf2f7;
                margin-top: 10px;
            }

            .footer .tech-stack {
                display: flex;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
                margin: 12px 0;
            }

            .footer .tech-item {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 14px;
                background: #f7fafc;
                border-radius: 100px;
                font-size: 12px;
                color: #4a5568;
                border: 1px solid #edf2f7;
            }

            .footer .tech-item i {
                color: #4f46e5;
            }

            .footer .highlight {
                color: #4f46e5;
                font-weight: 500;
            }

            .footer .heart {
                color: #e53e3e;
            }

            .footer .version-info {
                color: #a0aec0;
                font-size: 13px;
                margin-top: 8px;
            }

            /* Responsive */
            @media (max-width: 768px) {
                .card { padding: 30px; }
                .header h1 { font-size: 28px; }
                .grid { grid-template-columns: 1fr 1fr; }
                .stats { grid-template-columns: 1fr 1fr; }
                .logo-icon { width: 60px; height: 60px; font-size: 28px; }
            }

            @media (max-width: 480px) {
                .card { padding: 20px; }
                .grid { grid-template-columns: 1fr; }
                .stats { grid-template-columns: 1fr; }
                .header h1 { font-size: 24px; }
                .badge-container { flex-direction: column; align-items: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <!-- Header -->
                <div class="header">
                    <div class="logo-icon">🚀</div>
                    <h1>Habot<span>Connect</span></h1>
                    <p class="subtitle">Intelligent LSA Booking Platform — Connecting Parents with Learning Support Assistants</p>
                    <div class="badge-container">
                        <span class="badge"><span class="dot"></span> API v1.0</span>
                        <span class="badge"><i class="fas fa-shield-alt"></i> Secure</span>
                        <span class="badge"><i class="fas fa-bolt"></i> Fast</span>
                        <span class="badge"><i class="fas fa-mobile-alt"></i> Mobile Ready</span>
                    </div>
                </div>

                <!-- Stats -->
                <div class="stats">
                    <div class="stat-card">
                        <span class="number"><i class="fas fa-code"></i></span>
                        <span class="label">12 Endpoints</span>
                    </div>
                    <div class="stat-card">
                        <span class="number">100%</span>
                        <span class="label">Test Coverage</span>
                    </div>
                    <div class="stat-card">
                        <span class="number">v1</span>
                        <span class="label">Current Version</span>
                    </div>
                    <div class="stat-card">
                        <span class="number"><i class="fas fa-infinity"></i></span>
                        <span class="label">Always Available</span>
                    </div>
                </div>

                <!-- Endpoints -->
                <div class="section-title">
                    <i class="fas fa-plug"></i> Available Endpoints
                </div>

                <div class="grid">
                    <a href="/admin/" class="item">
                        <span class="icon">⚙️</span>
                        <span class="name">Admin</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/" class="item">
                        <span class="icon">📡</span>
                        <span class="name">API Root</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/users/" class="item">
                        <span class="icon">👤</span>
                        <span class="name">Users</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/profiles/" class="item">
                        <span class="icon">📋</span>
                        <span class="name">Profiles</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/lsa-profiles/" class="item">
                        <span class="icon">🧑‍🏫</span>
                        <span class="name">LSAs</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/availability/" class="item">
                        <span class="icon">📅</span>
                        <span class="name">Availability</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/bookings/" class="item">
                        <span class="icon">📝</span>
                        <span class="name">Bookings</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/reviews/" class="item">
                        <span class="icon">⭐</span>
                        <span class="name">Reviews</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/children/" class="item">
                        <span class="icon">👶</span>
                        <span class="name">Children</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/specializations/" class="item">
                        <span class="icon">🎯</span>
                        <span class="name">Specializations</span>
                        <span class="method method-get">GET</span>
                    </a>
                    <a href="/api/v1/auth/login/" class="item item-special">
                        <span class="icon">🔑</span>
                        <span class="name">Login</span>
                        <span class="method method-post">POST</span>
                    </a>
                    <a href="/api/v1/auth/logout/" class="item item-danger">
                        <span class="icon">🚪</span>
                        <span class="name">Logout</span>
                        <span class="method method-post">POST</span>
                    </a>
                </div>

                <!-- Footer -->
                <div class="footer">
                    <div class="tech-stack">
                        <span class="tech-item"><i class="fab fa-python"></i> Django 4.2</span>
                        <span class="tech-item"><i class="fas fa-code"></i> DRF 3.14</span>
                        <span class="tech-item"><i class="fas fa-database"></i> PostgreSQL</span>
                        <span class="tech-item"><i class="fas fa-lock"></i> JWT Auth</span>
                    </div>
                    <p>
                        ⚡ Built with <span class="highlight">Django REST Framework</span> &nbsp;·&nbsp;
                        <span class="heart">❤️</span> for LSAs &amp; Parents
                    </p>
                    <div class="version-info">
                        <i class="far fa-copyright"></i> 2026 HabotConnect &nbsp;·&nbsp;
                        <i class="fas fa-code-branch"></i> v1.0.0 &nbsp;·&nbsp;
                        <i class="fas fa-clock"></i> <span id="datetime"></span>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Live datetime
            function updateDateTime() {
                const now = new Date();
                const options = { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric', 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit',
                    timeZoneName: 'short'
                };
                document.getElementById('datetime').textContent = now.toLocaleDateString('en-US', options);
            }
            updateDateTime();
            setInterval(updateDateTime, 1000);
        </script>
    </body>
    </html>
    """)

# Add this redirect view for /accounts/profile/
def redirect_to_home(request):
    return redirect('/')

urlpatterns = [
    path('', home),
    path('accounts/profile/', redirect_to_home),  # Redirect /accounts/profile/ to home
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
]