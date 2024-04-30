from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    changfreq = 'always'
    priority = 0.9

    def items(self):
        return Product.objects.order_by('id')

    def lastmod(self, obj):
        return obj.created_at
