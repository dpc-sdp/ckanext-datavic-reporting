jQuery(document).ready(function () {

    general_date_range_sub_organisations = $('#general_date_range_sub_organisations');
    general_date_range_sub_organisations.parent().parent().hide();

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
                        text: this.text
                    }).appendTo(sub_organisations);
                });
                sub_organisations.parent().parent().show();
            }
            else {
                sub_organisations.parent().parent().hide();
            }
        })
    }
});