from django.urls import path
from engine_app.views import HomeView, InstalledModulesView, ModuleDetailView, AdditionalFieldMetadataView, ProductDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('module/', InstalledModulesView.as_view(), name='installed_modules'),
    path("module/<int:module_id>/", ModuleDetailView.as_view(), name="module_detail"),
    path("module/<int:module_id>/additional-fields/", AdditionalFieldMetadataView.as_view(), name="additional_fields"),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
]
