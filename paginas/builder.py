import os
try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('PageBuilder')

def get_analytics_id():
    """Get Google Analytics ID from environment"""
    return os.getenv('ANALYTICS_ID', '')

def generate_ga4_script(analytics_id):
    """Generate Google Analytics 4 script tag"""
    if not analytics_id or analytics_id == 'G-XXXXXXXXXX':
        logger.info("Google Analytics ID not configured. Skipping GA4 injection.")
        return "<!-- Google Analytics not configured -->"
    
    script = f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={analytics_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{analytics_id}');
  
  // Custom event helpers
  function trackEvent(eventName, params) {{
    if (typeof gtag === 'function') {{
      gtag('event', eventName, params);
      console.log('GA4 Event:', eventName, params);
    }} else {{
      console.log('GA4 not loaded, event not tracked:', eventName);
    }}
  }}
</script>
"""
    logger.info(f"GA4 script generated for {analytics_id}")
    return script

class PageBuilder:
    def __init__(self):
        self.template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline}</title>
    
    <!-- Google Analytics 4 -->
    {analytics_script}
    
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --dark-bg: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--dark-bg);
            color: var(--text-main);
            line-height: 1.6;
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Glassmorphism Header */
        header {{
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(10px);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 100;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .hero {{
            padding: 160px 0 100px;
            text-align: center;
            background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), transparent 40%),
                        radial-gradient(circle at bottom left, rgba(236, 72, 153, 0.15), transparent 40%);
        }}
        
        h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.2;
        }}
        
        .hero p {{
            font-size: 1.25rem;
            color: var(--text-muted);
            max-width: 700px;
            margin: 0 auto 40px;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 16px 40px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1.1rem;
            text-decoration: none;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(99, 102, 241, 0.4);
        }}

        .pain-section {{
            padding: 80px 0;
            background: var(--card-bg);
            margin: 40px 0;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.05);
        }}

        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 60px;
        }}

        .feature-card {{
            background: rgba(255,255,255,0.03);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.3s ease;
        }}
        
        .feature-card:hover {{
            background: rgba(255,255,255,0.05);
            transform: translateY(-5px);
        }}

        .feature-card h3 {{
            color: var(--primary);
            margin-bottom: 15px;
            font-size: 1.3rem;
        }}

        .pricing-section {{
            text-align: center;
            padding: 80px 0;
        }}

        .price-tag {{
            font-size: 4rem;
            font-weight: 700;
            color: white;
            margin: 20px 0;
        }}

        .guarantee {{
            margin-top: 40px;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        footer {{
            border-top: 1px solid rgba(255,255,255,0.1);
            padding: 40px 0;
            text-align: center;
            color: var(--text-muted);
            margin-top: 80px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            h1 {{ font-size: 2.5rem; }}
            .hero {{ padding: 120px 0 60px; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h2 style="font-size: 1.2rem; font-weight: 700;">{product_name}</h2>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>{headline}</h1>
            <p>{subheadline}</p>
            <a href="#pricing" class="cta-button" id="main-cta">{cta_text}</a>
        </div>
    </section>

    <section class="container pain-section">
        <div style="text-align: center; max-width: 800px; margin: 0 auto;">
            <h2 style="font-size: 2rem; margin-bottom: 20px;">{pain_agitation}</h2>
            <p style="font-size: 1.1rem; color: var(--text-muted);">{solution_promise}</p>
        </div>
    </section>

    <section class="container">
        <div class="features-grid">
            {benefits_html}
        </div>
    </section>

    <section class="pricing-section" id="pricing">
        <div class="container">
            <h2>Get Started Today</h2>
            <div class="price-tag">{pricing_text}</div>
            <a href="#" class="cta-button" onclick="startCheckout()">{cta_text}</a>
            <p class="guarantee">30-Day Money Back Guarantee • Instant Access</p>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2024 MicroProduct Systems. All rights reserved.</p>
        </div>
    </footer>

    <script>
        // Simple Frontend Telemetry with GA4 integration
        document.addEventListener('DOMContentLoaded', function() {
            console.log("Telemetry: Page Visit Recorded");
            
            // Track page view in GA4
            if (typeof trackEvent === 'function') {{
                trackEvent('page_view', {{
                    'page_title': document.title,
                    'page_location': window.location.href
                }});
            }}
            
            // In a real production env, you would send this to your backend
            // navigator.sendBeacon('/api/track', JSON.stringify({{type: 'visit'}}));
        }});

        function trackCheckout() {{
            console.log("Telemetry: Checkout Start Recorded");
            
            // Track checkout start in GA4
            if (typeof trackEvent === 'function') {{
                trackEvent('begin_checkout', {{
                    'currency': 'USD',
                    'value': parseFloat('{pricing_text}'.replace('$', '')),
                    'items': [{{
                        'item_name': '{product_name}',
                        'price': parseFloat('{pricing_text}'.replace('$', ''))
                    }}]
                }});
            }}
            
            // Track CTA click
            if (typeof trackEvent === 'function') {{
                trackEvent('cta_click', {{
                    'button_text': '{cta_text}',
                    'product_name': '{product_name}'
                }});
            }}
            
            // Backend tracking
            // navigator.sendBeacon('/api/track', JSON.stringify({{type: 'checkout_start'}}));
        }}
    </script>
</body>
</html>
"""

    def build_page(self, copy_data, product_name, output_path, checkout_url="#"):
        """
        Assembles the HTML with the provided copy.
        """
        if not copy_data:
            return None

        # Format benefits list
        benefits_html = ""
        for benefit in copy_data.get('benefits', []):
            benefits_html += f"""
            <div class="feature-card">
                <h3>Benefit</h3>
                <p>{benefit}</p>
            </div>
            """
        # If we have features, add them too or mix
        for feature in copy_data.get('features', []):
             benefits_html += f"""
            <div class="feature-card">
                <h3>Feature</h3>
                <p>{feature}</p>
            </div>
            """

        # Generate GA4 script
        analytics_id = get_analytics_id()
        analytics_script = generate_ga4_script(analytics_id)
        
        html = self.template.format(
            analytics_script=analytics_script,
            headline=copy_data.get('headline', 'Product Title'),
            subheadline=copy_data.get('subheadline', 'Product Subtitle'),
            pain_agitation=copy_data.get('pain_agitation', 'Problem?'),
            solution_promise=copy_data.get('solution_promise', 'Solution.'),
            cta_text=copy_data.get('cta_text', 'Buy Now'),
            pricing_text=copy_data.get('pricing_text', '$19'),
            product_name=product_name,
            benefits_html=benefits_html
        )
        
        # Inject checkout URL and update tracking
        html = html.replace('href="#"', f'href="{checkout_url}"')
        html = html.replace('onclick="startCheckout()"', 'onclick="trackCheckout()"')
        html = html.replace('id="main-cta"', '') 

        # Do NOT remove the script block anymore to enable telemetry.
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Page built at: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error building page: {e}")
            return None
