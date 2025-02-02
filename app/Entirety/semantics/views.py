from django.views.generic import TemplateView
from django.shortcuts import redirect
from projects.models import Project
from django.http import JsonResponse
import json
from projects.mixins import ProjectContextMixin
from semantics.prepDataSemantics import PrepData
from django.shortcuts import render
from entities.requests import get_entity


class SemanticsVisualizer(ProjectContextMixin, TemplateView):
    template_name = "semantics/semantics_visualize.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # PrepData.generate_df(self)
        context['elements'] = PrepData.generate_df(self)
        context['types'] = PrepData.types(self)
        context['relationships'] = PrepData.relationships(self)
        return context

    def post(self, request, project_id, *args, **kwargs):
        data = json.loads(request.body)
        entityID = (data['nodeID'])
        entity = get_entity(self, entityID, "", self.project)
        entity_json = json.loads(entity.json())
        table_data = []
        for key, value in entity_json.items():
            if isinstance(value, dict):
                val_type = value.get('type', '-')
                val_value = json.dumps(value.get('value', '-'))
                val_metadata = json.dumps(value.get('metadata', '-'))
                table_data.append({"Name": key, "Value": val_value, "Type": val_type, "Metadata": val_metadata})
            else:
                table_data.append({"Name": key, "Value": value, "Type": "-", "Metadata": "-"})

        return JsonResponse({'entity': table_data})

    def all_values(self, dict_obj, parent_key=''):
        """
        Recursively yields all keys and values in a nested dictionary.

        This function iterates over all key-value pairs in the given dictionary, and recursively
        yields all keys and values in any nested dictionaries. The yielded keys are generated by
        concatenating the parent key and the current key, separated by a dot ('.'), if applicable.

        Args:
            dict_obj (dict): The dictionary to extract keys and values from.
            parent_key (str, optional): The parent key to be used for nested dictionaries.
                Defaults to an empty string.

        Yields:
            tuple: A tuple containing the current key and value as (key, value).

        Example:
            >>> my_dict = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
            >>> for key, value in all_values(my_dict):
            ...     print(key, value)
            a 1
            b.c 2
            b.d.e 3

        """

        # Iterate over all key-value pairs in the passed dictionary
        for key, value in dict_obj.items():
            # Generate the current key by concatenating the parent key and the current key
            current_key = f"{parent_key}.{key}" if parent_key else key

            # If value is of dictionary type then recursively yield all keys and values
            # in that nested dictionary
            if isinstance(value, dict):
                yield from self.all_values(value, current_key)
            else:
                # Yield the current key and value as a tuple
                yield current_key, value


class LdVisualizer(ProjectContextMixin, TemplateView):
    templet_name = "semantics/semantics_LdVisualize.html"
