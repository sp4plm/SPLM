(function(win,undefined){
    var QueryTextEditor,
        clsStatusBar, QTEStatusBar,
        clsToolbar, QTEToolbar,
        domBuilder, _domData,
        _aceToolbarOpts,
        _button_acts_refs;


    function _ev_update_toolbar() {
        if (typeof void null != typeof _button_acts_refs && null != _button_acts_refs) {
//            _button_acts_refs.saveButton.disabled = QueryTextEditor.session.getUndoManager().isClean();
            _button_acts_refs.undoButton.disabled = !QueryTextEditor.session.getUndoManager().hasUndo();
            _button_acts_refs.redoButton.disabled = !QueryTextEditor.session.getUndoManager().hasRedo();
        }
    }

    function _ev_save() {
        localStorage.savedValue = QueryTextEditor.getValue();
        QueryTextEditor.session.getUndoManager().markClean();
        _ev_update_toolbar();
    }


    try {
        if (typeof void null != ace && null != ace) {
            QueryTextEditor = ace.edit("query-text-editor");
            domBuilder = ace.require("ace/lib/dom").buildDom;
        } else {
            alert('query_text_editor say -> No code editor lib');
        }

        _aceToolbarOpts = {
            "Font Size": {
                path: "fontSize",
                type: "number",
                defaultValue: 12,
                defaults: [
                    {caption: "12px", value: 12},
                    {caption: "24px", value: 24}
                ]
            },
            "Show Invisibles": {
                path: "showInvisibles"
            }
        };


        clsStatusBar = ace.require("ace/ext/statusbar").StatusBar;
        QTEStatusBar = new clsStatusBar(QueryTextEditor, document.getElementById("qte-statusbar"));

        QueryTextEditor.setOptions({
           enableBasicAutocompletion: true, // the editor completes the statement when you hit Ctrl + Space
           enableLiveAutocompletion: false, // the editor completes the statement while you are typing
           enableSnippets: false,
           showInvisibles: false,
           showPrintMargin: false, // hides the vertical limiting strip
           // maxLines: Infinity,
           fontSize: 12
//           fontSize: "100%" // ensures that the editor fits in the environment
        });

        QueryTextEditor.session.setMode("ace/mode/sparql");
        // QueryTextEditor.setTheme("ace/theme/twilight");
        _button_acts_refs = {};
        if (typeof function(){} == typeof _ev_update_toolbar) {
            QueryTextEditor.on("input", _ev_update_toolbar);
        }
        QueryTextEditor.session.setValue(localStorage.savedValue || "")

        domBuilder(["div", { class: "toolbar" },

            ["button", {
                ref: "undoButton",
                onclick: function() {
                    QueryTextEditor.undo();
                }
            }, "undo"],
            ["button", {
                ref: "redoButton",
                onclick: function() {
                    QueryTextEditor.redo();
                }
            }, "redo"],
             ["input", {type: "number", value: QueryTextEditor.getOption('fontSize'), style:"width:4em",
                defaultValue: 12,
                defaults: [
                    {caption: "12px", value: 12},
                    {caption: "24px", value: 24}
                ],
                ace_selected_button: true,
                'aria-pressed': false,
             oninput: function() {
                QueryTextEditor.renderer.setOption('fontSize', parseInt(this.value));
//                alert('input');
            }}],
            ["input",
                { type: "checkbox", id: 'showInvisibles',
                    label: 'Show Invisibles',
                    checked: QueryTextEditor.getOption('showInvisibles') || null,
                    onchange: function() {
                        var value = this.checked;
                        QueryTextEditor.renderer.setOption('showInvisibles', value);
                    }
                }]
        ], document.getElementById('qte-toolbar'), _button_acts_refs);
        //$('#qte-toolbar button').button();
    } catch(e) {
        alert(e);
    }
    if ('object' === typeof win && 'object' === typeof win.document) {
        win['QueryTextEditor'] = QueryTextEditor;
    }
}(window));