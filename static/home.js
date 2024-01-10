function toSixDigitHex(hexVal) {
    // Convert 3-digit hex value to 6-digit
    hexVal = hexVal.split('').map(function (hex) {
        return hex + hex;
    }).join('');
    hexVal = '#' + hexVal;
    return hexVal;
};

$(document).ready(function() {
    $('.inputs').on('input', function(e) {
        $.ajax({
        type: 'POST',
        url: '/',
        data: {
            'qrcode_data': $('#qrcode_data').val(),
            'gif_url': $('#qrcode_gif_url').val(),
            'color': $('#qrcode_color').val(),
            'color_acc': $('#qrcode_color_acc').val(),
            'bg_color': $('#qrcode_bg_color').val(),
            'bg_color_acc': $('#qrcode_bg_color_acc').val(),
            'border_size': $('#qrcode_border_size').val(),
            'scale': $('#qrcode_scale').val(),
        },
        success: function(response) {
            // Update qrcode
            $("#picture").attr("src", `data:image/png;base64,${response}`);
            // Update hex labels
            $('#color-val').text($('#qrcode_color').val());
            $('#color-acc-val').text($('#qrcode_color_acc').val());
            $('#bg-color-val').text($('#qrcode_bg_color').val());
            $('#bg-color-acc-val').text($('#qrcode_bg_color_acc').val());
            // Update hex color input values
            $('#qrcode_color_hex').val($('#qrcode_color').val());
            $('#qrcode_color_acc_hex').val($('#qrcode_color_acc').val());
            $('#qrcode_bg_color_hex').val($('#qrcode_bg_color').val());
            $('#qrcode_bg_color_acc_hex').val($('#qrcode_bg_color_acc').val());
        }
        });
    });

    $('.inputs-hex').on('input', function(e) {
        // Trigger when hex input fields are changed. Will update color picker and hex label values.
        var hexVals = {};
        $('.inputs-hex').each(function(i, obj) {
            hexVal = $(this).val().replace('#','');
            if (hexVal.length === 3) {
                hexVals[$(this).attr('id')] = toSixDigitHex(hexVal);
            } else {
                hexVals[$(this).attr('id')] = $(this).val();
            }
        });

        $.ajax({
        type: 'POST',
        url: '/',
        data: {
            'qrcode_data': $('#qrcode_data').val(),
            'gif_url': $('#qrcode_gif_url').val(),
            'color': hexVals['qrcode_color_hex'],
            'color_acc': hexVals['qrcode_color_acc_hex'],
            'bg_color': hexVals['qrcode_bg_color_hex'],
            'bg_color_acc': hexVals['qrcode_bg_color_acc_hex'],
            'border_size': $('#qrcode_border_size').val(),
            'scale': $('#qrcode_scale').val(),
        },
        success: function(response) {
            // Update qrcode
            $("#picture").attr("src", `data:image/png;base64,${response}`);
            // Update hex labels
            $('#color-val').text(hexVals['qrcode_color_hex']);
            $('#color-acc-val').text(hexVals['qrcode_color_acc_hex']);
            $('#bg-color-val').text(hexVals['qrcode_bg_color_hex']);
            $('#bg-color-acc-val').text(hexVals['qrcode_bg_color_acc_hex']);
            // Update color picker values
            $('#qrcode_color').val(hexVals['qrcode_color_hex']);
            $('#qrcode_color_acc').val(hexVals['qrcode_color_acc_hex']);
            $('#qrcode_bg_color').val(hexVals['qrcode_bg_color_hex']);
            $('#qrcode_bg_color_acc').val(hexVals['qrcode_bg_color_acc_hex']);
        }
        });
    });
});