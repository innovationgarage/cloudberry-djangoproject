(function ($) {
    oldHeight = 0,
    oldWidth = 0;

    var setupTabs = function(el) {
        var tabs = $(el).closest(".tab-parent").find(".nav-tabs");
        var tab_contents = $(el).closest(".tab-content");

        tabs.find(".json-editor-tab").remove();
            
        $(".span12[data-schemapath]").filter(function (idx, item) {
            return $(item).attr("data-schemapath").split(".").length == 2;
        }).map(function (idx, item) {
            item = $(item);
            var content = item.closest('.row-fluid');
            var header = content.find("> .span12 > h3");
            var id = item.attr("data-schemapath").replace('.', '-');
            var title = header.find("> span").text();
            if (!title) {
                title = item.attr("data-schemapath").split(".")[1];
            }
            var tab = $('<li class="nav-item json-editor-tab"></li>');
            tab.append('<a class="nav-link" id="json-editor-tab-' + id +
                       '" data-toggle="tab" href="#json-editor-' + id +
                       '" role="tab" aria-controls="' + title +
                       '" aria-selected="true">' + title +
                       '</a>');
            tabs.append(tab);

            header.addClass("json-editor-top-header");

            var tab_content_wrapper = $("#json-editor-" +id);
            if (!tab_content_wrapper.length) {
                tab_content_wrapper = $('<div class="tab-pane json-editor-tab-pane" id="json-editor-' +id + '" role="tabpanel" aria-labelledby="' + id + '-tab"><div>');
            }
            tab_content_wrapper.append(content);
            tab_contents.append(tab_content_wrapper);
        });
        $("*[data-schemapath='root'] .well").css({display: 'none'});
        $("*[data-schemapath='root'] .json-editor-btn-collapse").css({display: 'none'});
    };

    var setupModals = function (el) {
        var modals = $(el).find(".json-editor-edit-json-modal");
        $("body").append(modals);
    }
    
    var loadUi = function(el, schema, setInitialValue){
        var field = $(el),
            form = field.parents('form').eq(0),
            value = JSON.parse(field.val()),
            id = field.attr('id') + '_jsoneditor',
            initialField = $('#initial-' + field.attr('id')),
            container = field.parents('.form-row').eq(0),
            labelText = container.find('label:not(#netjsonconfig-hint)').text(),
            startval = $.isEmptyObject(value) ? null : value,
            editorContainer = $('#' + id),
            html, editor, options, wrapper, header,
            getEditorValue, updateRaw;
        // inject editor unless already present
        if(!editorContainer.length){
            html =  '<div class="jsoneditor-wrapper">';
            html += '<fieldset class="module aligned"><label class="required" for="' +  id + '">'+ labelText +'</label>';
            html += '<div id="'+ id +'" class="jsoneditor"></div></fieldset>';
            html += '</div>';
            container.hide().after(html);
            editorContainer = $('#' + id);
        }
        else{
            editorContainer.html('');
        }

        // stop operation if empty admin inline object
        if (field.attr('id').indexOf('__prefix__') > -1) {
            return;
        }

        wrapper = editorContainer.parents('.jsoneditor-wrapper');
        options = {
            theme: 'django',
            disable_collapse: true,
            disable_edit_json: true,
            startval: startval,
            keep_oneof_values: false,
            show_errors: 'change',
            schema: schema
        };
        if (field.attr("data-options") !== undefined) {
          $.extend(options, JSON.parse(field.attr("data-options")));
        }

        $(".json-editor-modal").remove();            
        $(".json-editor-tab").remove();            
        $("*[data-schemapath]").remove();
        
        editor = new JSONEditor(document.getElementById(id), options);
        getEditorValue = function(){
            return JSON.stringify(editor.getValue(), null, 4);
        };
        updateRaw = function(){
            field.val(getEditorValue());
        };

        // set initial field value to the schema default
        if (setInitialValue) {
            initialField.val(getEditorValue());
        }
        // update raw value on change event
        editor.on('change', updateRaw);

        // update raw value before form submit
        form.submit(function(e){
        });

        // allow to add object properties by pressing enter
        form.on('keypress', '.jsoneditor .modal input[type=text]', function(e){
            if(e.keyCode == 13){
                e.preventDefault();
                $(e.target).siblings('input.json-editor-btn-add').trigger('click');
                $(e.target).val('');
            }
        });

        editor.updateWidget = function () {
            setupModals(editorContainer);
            setupTabs(editorContainer);
        };
        editor.updateWidget();
    };

    var loadUiAndSchema = function(el, schema, setInitialValue){
        if (!schema) {
            loadUi(el, {}, setInitialValue);
        } else {
            $.getJSON(schema).success(function(schema){
                loadUi(el, schema, setInitialValue);
            });
        }
    };

    var bindLoadUi = function(){
        $('.jsoneditor-raw').each(function(i, el){
            var field = $(el),
                schema = field.attr("data-schema"),
                schema_selector = field.attr("data-schema-selector");
            if (schema !== undefined) {
                loadUi(el, schema, true);
            } else {
                if(schema_selector === undefined) {
                    schema_selector = '#id_backend, #id_config-0-backend';
                }
                var backend = $(schema_selector);
                // load first time
                loadUiAndSchema(el, backend.val(), true);
                // reload when backend is changed
                backend.change(function(){
                    loadUiAndSchema(el, backend.val());
                });
            }
        });
    };

    $(function() {
        var add_config = $('#config-group.inline-group .add-row');
        // if configuration is admin inline
        // load it when add button is clicked
        add_config.click(bindLoadUi);
        // otherwise load immediately
        bindLoadUi();
    });
}(django.jQuery));

var matchKey = (function () {
    var elem = document.documentElement;
    if (elem.matches) { return 'matches'; }
    if (elem.webkitMatchesSelector) { return 'webkitMatchesSelector'; }
    if (elem.mozMatchesSelector) { return 'mozMatchesSelector'; }
    if (elem.msMatchesSelector) { return 'msMatchesSelector'; }
    if (elem.oMatchesSelector) { return 'oMatchesSelector'; }
}());


var origJSONObjectEditor = JSONEditor.defaults.editors.object;
JSONEditor.defaults.editors.object = JSONEditor.defaults.editors.object.extend({
  build: function () {
      origJSONObjectEditor.prototype.build.apply(this, arguments);
      $(this.editjson_holder).addClass('json-editor-edit-json-modal');
      $(this.addproperty_holder).addClass('json-editor-add-property-modal');
  },
  addObjectProperty: function(name, prebuild_only) {
      origJSONObjectEditor.prototype.addObjectProperty.apply(this, arguments);
      if (!this.parent && this.jsoneditor.updateWidget) {
          this.jsoneditor.updateWidget();
      }
  },
  removeObjectProperty: function(property) {
      origJSONObjectEditor.prototype.removeObjectProperty.apply(this, arguments);
      if (!this.parent && this.jsoneditor.updateWidget) {
          this.jsoneditor.updateWidget();
      }
  }  
});

// JSON-Schema Edtor django theme
JSONEditor.defaults.themes.django = JSONEditor.defaults.themes.bootstrap2.extend({
    getButtonHolder: function() {
      return JSONEditor.defaults.themes.bootstrap2.prototype.getButtonHolder.apply(this, arguments);
    },
    getModal: function() {
      var el = document.createElement('div');
      el.className = 'json-editor-modal';
      el.style.display = 'none';
      return el;
    }    
});
