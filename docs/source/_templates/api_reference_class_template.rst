{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

   {% block methods %}
   .. automethod:: __init__

   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
   {% for item in methods %}
      {%- if item not in inherited_members %}
      ~{{ name }}.{{ item }}
      {%- endif %}
   {%- endfor %}

   .. rubric:: {{ _('Inherited Methods') }}

   .. autosummary::
   {% for item in methods %}
      {%- if item in inherited_members %}
      ~{{ name }}.{{ item }}
      {%- endif %}
   {%- endfor %}

   {% endif %}
   {% endblock %}


   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      {%- if item not in inherited_members %}
      ~{{ name }}.{{ item }}
      {%- endif %}
   {%- endfor %}

   .. rubric:: {{ _('Inherited Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      {%- if item in inherited_members %}
      ~{{ name }}.{{ item }}
      {%- endif %}
   {%- endfor %}

   {% endif %}
   {% endblock %}
