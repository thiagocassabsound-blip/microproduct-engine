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
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .glass {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
        .gradient-text {{ background: linear-gradient(135deg, #6366f1, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        
        /* A/B Test Variants - Hidden by default to prevent flash */
        .variant-a, .variant-b {{ display: none; }}
    </style>
</head>
<body class="bg-slate-900 text-slate-100 antialiased overflow-x-hidden">

    <!-- A/B Logic Script -->
    <script>
        // Simple client-side split testing
        const variant = Math.random() < 0.5 ? 'A' : 'B';
        document.documentElement.setAttribute('data-variant', variant);
        console.log("A/B Test Assigned Variant:", variant);
        
        document.addEventListener('DOMContentLoaded', () => {{
            document.querySelectorAll(`.variant-${{variant.toLowerCase()}}`).forEach(el => el.style.display = 'block');
            document.querySelectorAll('.variant-common').forEach(el => el.style.display = 'block');
            
            // Track assignment
            if (typeof trackEvent === 'function') {{
                trackEvent('ab_assignment', {{ 'variant': variant }});
            }}
        }});
    </script>

    <!-- Navigation -->
    <nav class="fixed w-full z-50 transition-all duration-300 glass">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-20">
                <span class="text-xl font-bold tracking-tight text-white">{product_name}</span>
                <a href="#pricing" class="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-full font-medium transition shadow-lg shadow-indigo-600/30 text-sm">
                    Get Access
                </a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        <!-- Background Glow -->
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full z-0 pointer-events-none">
            <div class="absolute top-20 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-[100px]"></div>
            <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600/20 rounded-full blur-[100px]"></div>
        </div>

        <div class="relative z-10 max-w-4xl mx-auto px-4 text-center">
            
            <!-- VARIANT A: Benefit Focused -->
            <div class="variant-a">
                <span class="inline-block py-1 px-3 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-6">
                    🚀 Proven Strategy
                </span>
                <h1 class="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
                    {headline}
                </h1>
            </div>

            <!-- VARIANT B: Urgency/Problem Focused -->
            <div class="variant-b">
                <span class="inline-block py-1 px-3 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-sm font-medium mb-6">
                    🔥 Limited Availability
                </span>
                <h1 class="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
                    Stop Losing Time. <span class="gradient-text">{headline}</span>
                </h1>
            </div>

            <p class="text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                {subheadline}
            </p>

            <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                <a href="#pricing" onclick="trackCheckout()" class="w-full sm:w-auto bg-white text-slate-900 px-8 py-4 rounded-full font-bold text-lg hover:bg-slate-100 transition shadow-xl hover:scale-105 transform duration-200">
                    {cta_text}
                </a>
                <span class="text-sm text-slate-500 flex items-center gap-2">
                    <i data-lucide="check-circle" class="w-4 h-4 text-emerald-500"></i> Instant Access
                </span>
            </div>
        </div>
    </section>

    <!-- Social Proof / Trust -->
    <section class="py-10 border-y border-slate-800 bg-slate-900/50">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p class="text-sm text-slate-500 font-medium mb-6 uppercase tracking-wider">Trusted by professionals</p>
            <div class="flex flex-wrap justify-center gap-12 opacity-50 grayscale hover:grayscale-0 transition duration-500">
               <!-- Placeholders for logos -->
               <div class="text-xl font-bold text-slate-300">ACME Corp</div>
               <div class="text-xl font-bold text-slate-300">GlobalTech</div>
               <div class="text-xl font-bold text-slate-300">IndieMaker</div>
               <div class="text-xl font-bold text-slate-300">SaaS Inc</div>
            </div>
        </div>
    </section>

    <!-- Problem/Agitation -->
    <section class="py-24 bg-slate-900">
        <div class="max-w-3xl mx-auto px-4">
            <div class="glass rounded-2xl p-8 md:p-12 border border-slate-700/50 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-red-500/5 rounded-full blur-[80px]"></div>
                
                <h2 class="text-3xl font-bold mb-6 text-white relative z-10">Does this sound familiar?</h2>
                <p class="text-xl text-slate-300 leading-relaxed mb-6 font-light">
                    {pain_agitation}
                </p>
                <div class="h-px w-full bg-gradient-to-r from-transparent via-slate-700 to-transparent my-8"></div>
                <p class="text-lg text-indigo-400 font-medium">
                    {solution_promise}
                </p>
            </div>
        </div>
    </section>

    <!-- Benefits Grid -->
    <section class="py-24 relative">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <h2 class="text-3xl md:text-5xl font-bold mb-6">Everything you need</h2>
                <p class="text-slate-400 max-w-2xl mx-auto">Designed to solve your specific challenges immediately.</p>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8">
                {benefits_html}
            </div>
        </div>
    </section>

    <!-- Pricing -->
    <section id="pricing" class="py-24 bg-slate-900 overflow-hidden relative">
        <div class="max-w-md mx-auto px-4 relative z-10">
            <div class="glass rounded-3xl p-1 border border-indigo-500/30 shadow-2xl shadow-indigo-500/10">
                <div class="bg-slate-900/90 rounded-[22px] p-8 md:p-12 text-center">
                    <span class="bg-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider mb-4 inline-block">
                        One-time Payment
                    </span>
                    <h3 class="text-xl text-slate-300 mb-2">Lifetime Access</h3>
                    <div class="text-6xl font-bold text-white mb-2 tracking-tight">
                        {pricing_text}
                    </div>
                    <p class="text-slate-500 text-sm mb-8">SECURE PAYMENT VIA STRIPE</p>
                    
                    <a href="#" onclick="trackCheckout()" class="block w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-lg py-4 rounded-xl transition shadow-lg shadow-indigo-600/25 mb-6">
                        {cta_text}
                    </a>
                    
                    <ul class="text-left space-y-3 text-slate-400 text-sm mb-8">
                        <li class="flex items-center gap-2">
                            <i data-lucide="check" class="w-4 h-4 text-emerald-500"></i> Instant Digital Delivery
                        </li>
                        <li class="flex items-center gap-2">
                            <i data-lucide="check" class="w-4 h-4 text-emerald-500"></i> 100% Satisfaction Guarantee
                        </li>
                        <li class="flex items-center gap-2">
                            <i data-lucide="check" class="w-4 h-4 text-emerald-500"></i> Secure Encryption
                        </li>
                    </ul>

                    <div class="text-xs text-slate-600 pt-6 border-t border-slate-800">
                        30-Day Money Back Guarantee. No questions asked.
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="py-12 border-t border-slate-800 text-center text-slate-500 text-sm">
        <p>&copy; 2024 MicroProduct Systems. All rights reserved.</p>
    </footer>

    <script>
        lucide.createIcons();
        
        function trackCheckout() {{
            console.log("Telemetry: Checkout Start");
            if (typeof trackEvent === 'function') {{
                trackEvent('begin_checkout', {{
                    'value': parseFloat('{pricing_text}'.replace(/[^0-9.]/g, '')),
                    'currency': 'USD',
                    'variant': document.documentElement.getAttribute('data-variant')
                }});
                
                trackEvent('cta_click', {{
                    'location': 'pricing_section'
                }});
            }}
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
            <div class="glass p-8 rounded-2xl hover:bg-white/5 transition duration-300 group">
                <div class="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition duration-300">
                    <i data-lucide="check" class="text-indigo-400 w-6 h-6"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-3">Core Benefit</h3>
                <p class="text-slate-400 leading-relaxed">{benefit}</p>
            </div>
            """
        # If we have features, add them too or mix
        for feature in copy_data.get('features', []):
             benefits_html += f"""
            <div class="glass p-8 rounded-2xl hover:bg-white/5 transition duration-300 group">
                <div class="w-12 h-12 bg-pink-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition duration-300">
                    <i data-lucide="zap" class="text-pink-400 w-6 h-6"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-3">Feature</h3>
                <p class="text-slate-400 leading-relaxed">{feature}</p>
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
