Date.prototype.format = function (format) {
    let date = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S+": this.getMilliseconds()
    };
    if (/(y+)/i.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    for (var k in date) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1
                ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
        }
    }
    return format;
};


function dateFormatPrint(date) {
    date = new Date(date)
    let format = 'yyyy-MM-dd hh:mm:ss';
    return date.format(format);
}


function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function ToastBuilder(options) {
    var style = $('<style>.toast {  padding: 15px 20px;  color: #fff;  background: rgba(0,0,10,0.7);  display: inline-block;  position: fixed;  top: -100px;  right: 15px;  opacity: 0;  transition: all 0.4s ease-out;}</style>');
    $('html > head').append(style);
    // options are optional
    var opts = options || {};

    // setup some defaults
    opts.defaultText = opts.defaultText || 'default text';
    opts.displayTime = opts.displayTime || 3000;
    opts.target = opts.target || 'body';

    return function (text) {
        $('<div/>')
            .addClass('toast')
            .prependTo($(opts.target))
            .text(text || opts.defaultText)
            .queue(function (next) {
                $(this).css({
                    'opacity': 1
                });
                var topOffset = 15;
                $('.toast').each(function () {
                    var $this = $(this);
                    var height = $this.outerHeight();
                    var offset = 15;
                    $this.css('top', topOffset + 'px');

                    topOffset += height + offset;
                });
                next();
            })
            .delay(opts.displayTime)
            .queue(function (next) {
                var $this = $(this);
                var width = $this.outerWidth() + 20;
                $this.css({
                    'right': '-' + width + 'px',
                    'opacity': 0
                });
                next();
            })
            .delay(600)
            .queue(function (next) {
                $(this).remove();
                next();
            });
    };

}
