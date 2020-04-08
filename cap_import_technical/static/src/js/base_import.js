odoo.define('cap_import_technical.import', function (require) {
    "use strict";

    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var DataImport = require('base_import.import').DataImport;
    DataImport.include({
        setup_encoding_picker: function () {
            this.$('input.oe_import_encoding').select2({
                width: '160px',
                query: function (q) {
                    var make = function (term) {
                        return {id: term, text: term};
                    };
                    var suggestions = _.map(
                        ('utf-8 utf-16 windows-1252 latin1 latin2 big5 ' +
                            'gb18030 shift_jis windows-1251 koir8_r').split(/\s+/),
                        make);
                    if (q.term) {
                        suggestions.unshift(make(q.term));
                    }
                    q.callback({results: suggestions});
                },
                initSelection: function (e, c) {
                    console.log("Im changing the default value utf-8");
                    return c({id: 'latin1', text: 'latin1'});
                }
            }).select2('val', 'latin1');
        }
    });

});