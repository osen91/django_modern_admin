/*global showAddAnotherPopup, showRelatedObjectLookupPopup showRelatedObjectPopup updateRelatedObjectLinks*/

(function($) {
    'use strict';
    jQuery(document).ready(function() {
        var modelName = jQuery('#django-admin-form-add-constants').data('modelName');
        jQuery('body').on('click', '.add-another', function(e) {
            e.preventDefault();
            var event = jQuery.Event('django:add-another-related');
            jQuery(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                showAddAnotherPopup(this);
            }
        });

        if (modelName) {
            jQuery('form#' + modelName + '_form :input:visible:enabled:first').focus();
        }
    });
})(django.jQuery);
