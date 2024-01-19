function toSixDigitHex(hexVal) {
    // Convert 3-digit hex value to 6-digit
    hexVal = hexVal.split('').map(function (hex) {
        return hex + hex;
    }).join('');
    hexVal = '#' + hexVal;
    return hexVal;
};

$(document).ready(function() {
    $('.inputs.color-picker').on('input', function(e) {
        curInput = $(this);
        // Update hex label
        newColorPickerVal = curInput.val();
        curInput.parent().parent().children('.hex-label').text(newColorPickerVal);
        // Update hex input field value
        curInput.parent().parent().children('.hex-field').val(newColorPickerVal);
        // Color picker has built-in functionality to prevent invalid values.
        // No error catching needed here.
    });

    $('.inputs.hex-field').on('input', function(e) {
        curInput = $(this);
        hexVal = curInput.val().replace('#','');
        newHexVal = '';
        if ((hexVal.length === 3 || hexVal.length === 6) && !isNaN(Number('0x' + hexVal))) {
            newHexVal = hexVal.length === 3 ? toSixDigitHex(hexVal) : '#' + hexVal;
            // Update hex label
            curInput.parent().children('.hex-label').text(newHexVal);
            // Update color picker value
            curInput.parent().children('.color-picker-wrap').children('.color-picker').val(newHexVal);
            // Hide invalid icon on success
            curInput.parent().children('.invalid-icon').children('.bi').hide();
        } 
        else {
            newHexVal = 'INVALID';
            // Update hex label
            curInput.parent().children('.hex-label').text(newHexVal);
            // Display invalid icon on failure
            curInput.parent().children('.invalid-icon').children('.bi').show();
        }
    });

    // Color picker and hex field code must be updated first (above) 
    // before AJAX request (below).
    $('.inputs').on('input', function(e) {
        curInput = $(this);
        data = {
            'qrcode_data': $('#qrcode_data').val(),
            'gif_url': $('#qrcode_gif_url').val(),
            'color': $('#qrcode_color').val(),
            'color_acc': $('#qrcode_color_acc').val(),
            'bg_color': $('#qrcode_bg_color').val(),
            'bg_color_acc': $('#qrcode_bg_color_acc').val(),
            'border_size': $('#qrcode_border_size').val(),
            'scale': $('#qrcode_scale').val(),
        };
        $.ajax({
            type: 'POST',
            url: '/',
            data: data,
            success: function(response) {
                // Update qrcode
                $("#picture").attr("src", `data:image/png;base64,${response}`);
            },
            error: function() {

            }
        });
    });
});