odoo.define('purchase_comparison_chart_v2.purchase_comparison_chart_v2', function() {

    require('web.dom_ready');

    $(".exe_radio").change(function() {

        var vendor_price = parseFloat($(this).parent().find('.exe_price').attr('initial_value').replace(",", ""));

        var ex_total = parseFloat($(this).parent().parent().find('.new_exe_budget').attr('initial_value').replace(",", ""));
        var current_qty = parseFloat($(this).parent().parent().find('.current_qty').text().replace(",", ""));
        alert(vendor_price + '--' + ex_total + '--' + current_qty);
        $(this).parent().parent().find('.new_exe_budget').text(
            ((((vendor_price * current_qty) + ex_total))).toFixed(2).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,")
        );

    });

    $('.supplier').click(function() {
        var supplier = ($(this).attr('class').split("_")[1]);
        $('.supplier_product_' + supplier).prop('checked', this.checked);
        $(".sale_tbody .row2").each(function() {
            var vendor_price = parseFloat($(this).find('.supplier_product_' + supplier).parent().find('.exe_price').attr('initial_value').replace(",", ""));
            if (!isNaN(vendor_price)) {
                var ex_total = parseFloat($(this).find('.new_exe_budget').attr('initial_value').replace(",", ""));
                var current_qty = parseFloat($(this).find('.current_qty').text().replace(",", ""));
                $(this).find('.new_exe_budget').text(
                    ((((vendor_price * current_qty) + ex_total))).toFixed(2).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,")
                );
            }

        });

    });


    $('.confirm_order').click(function() {
        var anyBoxesChecked = false;
        $('#purchase_comparision_from input[type="radio"]').each(function() {
            if ($(this).is(":checked")) {
                anyBoxesChecked = true;
            }
        });

        if (anyBoxesChecked == false) {
            alert('Please select at least one product');
            return false;
        }
    });
});