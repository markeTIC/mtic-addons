(function() {
    "use strict";

    var website = openerp.website;
    var _t = openerp._t;

    website.EditorBarContent.include({
        new_edition: function() {
            website.prompt({
                id: "editor_new_edition",
                window_title: _t("Nueva edición"),
                input: "Nombre de la edición",
            }).then(function (edition_name) {
                website.form('/edition/add_edition', 'POST', {
                    edition_name: edition_name
                });
            });
        },
    });
})();
