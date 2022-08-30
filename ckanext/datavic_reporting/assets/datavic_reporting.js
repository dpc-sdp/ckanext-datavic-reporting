jQuery(document).ready(function () {

    general_date_range_sub_organisations = $('#general_date_range_sub_organisations');


    if (!jQuery(general_date_range_sub_organisations).parent().parent().hasClass('no-hide')) {
        general_date_range_sub_organisations.parent().parent().hide();
    }

    jQuery('#general_date_range_organisations').on('change', function (e) {
        getSubOrganisations(this.value, general_date_range_sub_organisations);
    });

    general_year_month_sub_organisations = $('#general_year_month_sub_organisations');
    general_year_month_sub_organisations.parent().parent().hide();

    jQuery('#general_year_month_organisations').on('change', function (e) {
        getSubOrganisations(this.value, general_year_month_sub_organisations);
    });

    function getSubOrganisations(organisation_id, sub_organisations) {
        jQuery.getJSON('/user/reports/sub_organisations', { 'organisation_id': organisation_id }, function (data) {
            sub_organisations.empty();
            if (data.length > 1) {
                $(data).each(function () {
                    $("<option />", {
                        val: this.value,
                        text: this.text,
                        disabled: this.has_access == false
                    }).appendTo(sub_organisations);
                });
                sub_organisations.parent().parent().show();
            }
            else {
                sub_organisations.parent().parent().hide();
            }
        })
    }

    jQuery("#display-report").on('click', function() {
        jQuery("#option-display-report").prop("checked", true);
        jQuery(this).closest("form").submit();
        return false;
    });

    jQuery("#download-report").on('click', function() {
        jQuery("#option-download-report").prop("checked", true);
        jQuery(this).closest("form").submit();
        return false;
    });
});