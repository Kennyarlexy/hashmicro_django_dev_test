import subprocess
import os
import shutil

from django.shortcuts import redirect, render
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.conf import settings
from django.db.models import Q, Prefetch

from engine_app import utils
from engine_app.forms import RoleForm, ModuleForm, ProductForm, AdditionalFieldMetadataForm
from engine_app.models import InstalledModule, Product, RoleChoices, AdditionalFieldMetadata, AdditionalFieldDataType, AdditionalFieldInt, AdditionalFieldStr

class HomeView(FormView):
    template_name = 'engine_app/home.html'
    form_class    = RoleForm
    success_url   = reverse_lazy('installed_modules')

    def form_valid(self, form: RoleForm):
        selected_role = int(form.cleaned_data['role'])
        self.request.session['role'] = selected_role
        self.request.session['role_name'] = utils.get_role_name(selected_role)

        return super().form_valid(form)
    

class InstalledModulesView(TemplateView):
    template_name = 'engine_app/installed_modules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.request.session.get('role')
        context['role_name'] = self.request.session.get('role_name')
        context['role_choices'] = RoleChoices
        context['installed_module_objs'] = InstalledModule.objects.all()
        context['form'] = kwargs.get('form', ModuleForm())

        return context
    
    def post(self, request, *args, **kwargs):
        if uninstalled_module_id := request.POST.get('uninstalled_module_id'):
            self.handle_uninstalled_app(int(uninstalled_module_id))
            return redirect('installed_modules')
        
        form = ModuleForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        module_name = form.cleaned_data['name']
        app_path = os.path.join(settings.BASE_DIR, module_name)

        if os.path.exists(app_path):
            form.add_error('name', 'A module with this name already exists.')
            return self.render_to_response(self.get_context_data(form=form))
        
        try:
            subprocess.run(['django-admin', 'startapp', module_name], check=True, cwd=settings.BASE_DIR)
        except subprocess.CalledProcessError:
            form.add_error('name', 'Failed to create the module for unknown reason')
            return self.render_to_response(self.get_context_data(form=form))

        self.register_app_in_installed_apps(module_name)
        saved_module_obj = form.save()

        return redirect('module_detail', module_id=saved_module_obj.id)

    def register_app_in_installed_apps(self, module_name: str) -> None:
        settings.INSTALLED_APPS.append(module_name)

    def handle_uninstalled_app(self, uninstalled_module_id: int) -> None:
        uninstalled_module_obj = InstalledModule.objects.get(id=uninstalled_module_id)

        app_path = os.path.join(settings.BASE_DIR, uninstalled_module_obj.name)
        if os.path.exists(app_path):
            shutil.rmtree(app_path)

        self.handle_deleted_barcode_files(uninstalled_module_id)
        uninstalled_module_obj.delete()

    def handle_deleted_barcode_files(self, uninstalled_module_id: int) -> None:
        deleted_product_objs = list(Product.objects.filter(module_id=uninstalled_module_id))
        
        for deleted_product_obj in deleted_product_objs:
            if deleted_product_obj.barcode and default_storage.exists(deleted_product_obj.barcode.path):
                default_storage.delete(deleted_product_obj.barcode.path)
        

class ModuleDetailView(TemplateView):
    template_name = 'engine_app/module_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_id = kwargs.get('module_id')
        context['role'] = self.request.session.get('role')
        context['role_name'] = self.request.session.get('role_name')
        context['role_choices'] = RoleChoices
        context['product_objs'] = Product.objects.filter(module_id=module_id)
        context['form'] = kwargs.get('form', ProductForm())
        context['additional_field_objs'] = self.get_additional_field_objs(module_id)

        return context
    
    def post(self, request, **kwargs):
        module_id = kwargs.get('module_id')

        if delete_product_id := request.POST.get('delete_product_id'):
            self.handle_post_delete(int(delete_product_id))
            return redirect('module_detail', module_id=module_id)
        
        form = ProductForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        
        product = form.save(commit=False)
        product.module_id = module_id
        product.save()

        metadata_objs = self.get_additional_field_objs(module_id)

        int_additional_fields, str_additional_fields = [], []
        for metadata_obj in metadata_objs:
            key   = f'additional_field_{metadata_obj.id}'
            value = request.POST.get(key)

            if metadata_obj.data_type == AdditionalFieldDataType.INT:
                int_additional_fields.append(
                    AdditionalFieldInt(metadata=metadata_obj, product=product, value=int(value))
                )
            else:
                str_additional_fields.append(
                    AdditionalFieldStr(metadata=metadata_obj, product=product, value=value)
                )

        AdditionalFieldInt.objects.bulk_create(int_additional_fields)
        AdditionalFieldStr.objects.bulk_create(str_additional_fields)

        return redirect('module_detail', module_id=module_id)
    
    def get_additional_field_objs(self, module_id: int) -> list[AdditionalFieldMetadata]:
        additional_field_objs = list(AdditionalFieldMetadata.objects.filter(module_id=module_id))
        return additional_field_objs
    
    def handle_post_delete(self, deleted_product_id: int) -> None:
        deleted_product_obj = Product.objects.get(id=deleted_product_id)

        if deleted_product_obj.barcode and default_storage.exists(deleted_product_obj.barcode.path):
            default_storage.delete(deleted_product_obj.barcode.path)

        deleted_product_obj.delete()


class AdditionalFieldMetadataView(TemplateView):
    template_name = "engine_app/additional_fields.html"

    def get_context_data(self, **kwargs):
        module_id = kwargs.get('module_id')
        context = super().get_context_data(**kwargs)

        context['role_name'] = self.request.session.get('role_name')
        context['module_id'] = module_id
        context['field_metadata_objs'] = AdditionalFieldMetadata.objects.filter(module_id=module_id)
        context['form'] = AdditionalFieldMetadataForm()

        return context

    def post(self, request, **kwargs):
        module_id = kwargs.get('module_id')
        module = InstalledModule.objects.get(id=module_id)
        
        form = AdditionalFieldMetadataForm(request.POST)
        if form.is_valid():
            field_metadata = form.save(commit=False)
            field_metadata.module = module
            field_metadata.save()
            return redirect('additional_fields', module_id=module_id)

        return self.render_to_response(self.get_context_data(form=form))


class ProductDetailView(View):
    template_name = 'engine_app/product_detail.html'

    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        fields_metadata = AdditionalFieldMetadata.objects.filter(module_id=product.module_id)

        int_fields_metadata = fields_metadata.filter(data_type=AdditionalFieldDataType.INT)
        str_fields_metadata = fields_metadata.filter(data_type=AdditionalFieldDataType.STRING)

        int_field_metadata_with_value_objs = list(
            int_fields_metadata.prefetch_related(
                Prefetch(
                    'additionalfieldint_set', 
                    queryset=AdditionalFieldInt.objects.filter(product_id=product_id),
                    to_attr='value'
                )
            )
        )

        str_field_metadata_with_value_objs = list(
            str_fields_metadata.prefetch_related(
                Prefetch(
                    'additionalfieldstr_set', 
                    queryset=AdditionalFieldStr.objects.filter(product_id=product_id),
                    to_attr='value'
                )
            )
        )

        context = {
            'module_id': product.module_id,
            'role_name': self.request.session.get('role_name'),
            'product': product,
            'additional_field_objs': int_field_metadata_with_value_objs + str_field_metadata_with_value_objs,
        }

        return render(request, self.template_name, context)
