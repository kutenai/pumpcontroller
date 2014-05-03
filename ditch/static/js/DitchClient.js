/**
 * Created with IntelliJ IDEA.
 * User: kutenai
 * Date: 8/13/12
 * Time: 10:01 PM
 * To change this template use File | Settings | File Templates.
 */

var DitchClient = {

    VERSION: '1.0.0',

    /**
     * Variable: IS_IE
     *
     * True if the current browser is Internet Explorer.
     */
    IS_IE: navigator.userAgent.indexOf('MSIE') >= 0,

    /**
     * Variable: IS_IE6
     *
     * True if the current browser is Internet Explorer 6.x.
     */
    IS_IE6: navigator.userAgent.indexOf('MSIE 6') >= 0,

    /**
     * Variable: IS_NS
     *
     * True if the current browser is Netscape (including Firefox).
     */
    IS_NS: navigator.userAgent.indexOf('Mozilla/') >= 0 &&
        navigator.userAgent.indexOf('MSIE') < 0,

    /**
     * Variable: IS_OP
     *
     * True if the current browser is Opera.
     */
    IS_OP: navigator.userAgent.indexOf('Opera/') >= 0,

    /**
     * Variable: IS_OT
     *
     * True if -o-transform is available as a CSS style. This is the case
     * for Opera browsers that use Presto/2.5 and later.
     */
    IS_OT: navigator.userAgent.indexOf('Presto/2.4.') < 0 &&
               navigator.userAgent.indexOf('Presto/2.3.') < 0 &&
               navigator.userAgent.indexOf('Presto/2.2.') < 0 &&
               navigator.userAgent.indexOf('Presto/2.1.') < 0 &&
               navigator.userAgent.indexOf('Presto/2.0.') < 0 &&
        navigator.userAgent.indexOf('Presto/1.') < 0,

    /**
     * Variable: IS_SF
     *
     * True if the current browser is Safari.
     */
    IS_SF: navigator.userAgent.indexOf('AppleWebKit/') >= 0 &&
        navigator.userAgent.indexOf('Chrome/') < 0,

    /**
     * Variable: IS_GC
     *
     * True if the current browser is Google Chrome.
     */
    IS_GC: navigator.userAgent.indexOf('Chrome/') >= 0,

    /**
     * Variable: IS_MT
     *
     * True if -moz-transform is available as a CSS style. This is the case
     * for all Firefox-based browsers newer than or equal 3, such as Camino,
     * Iceweasel, Seamonkey and Iceape.
     */
    IS_MT: (navigator.userAgent.indexOf('Firefox/') >= 0 &&
        navigator.userAgent.indexOf('Firefox/1.') < 0 &&
        navigator.userAgent.indexOf('Firefox/2.') < 0) ||
               (navigator.userAgent.indexOf('Iceweasel/') >= 0 &&
                   navigator.userAgent.indexOf('Iceweasel/1.') < 0 &&
                   navigator.userAgent.indexOf('Iceweasel/2.') < 0) ||
               (navigator.userAgent.indexOf('SeaMonkey/') >= 0 &&
                   navigator.userAgent.indexOf('SeaMonkey/1.') < 0) ||
        (navigator.userAgent.indexOf('Iceape/') >= 0 &&
            navigator.userAgent.indexOf('Iceape/1.') < 0),

    IS_MAC: navigator.userAgent.toUpperCase().indexOf('MACINTOSH') > 0,

    /**
     * Variable: IS_TOUCH
     *
     * True if this client uses a touch interface (no mouse). Currently this
     * detects IPads, IPods, IPhones and Android devices.
     */
    IS_TOUCH: navigator.userAgent.toUpperCase().indexOf('IPAD') > 0 ||
                  navigator.userAgent.toUpperCase().indexOf('IPOD') > 0 ||
                  navigator.userAgent.toUpperCase().indexOf('IPHONE') > 0 ||
        navigator.userAgent.toUpperCase().indexOf('ANDROID') > 0,

    /**
     * Variable: IS_LOCAL
     *
     * True if the documents location does not start with http:// or https://.
     */
    IS_LOCAL: document.location.href.indexOf('http://') < 0 &&
        document.location.href.indexOf('https://') < 0,


    URLS : {},

    getUrl : function(key) {
        if (key in this.URLS) {
            return this.URLS[key];
        }
        return this.URLS['home'];
    },

    include: function(src)
    {
        document.write('<script src="'+src+'"></script>');
    }

};

if (typeof(BasePath) !== 'undefined' && BasePath.length > 0)
{
    // Adds a trailing slash if required
    if (BasePath.substring(BasePath.length - 1) == '/')
    {
        BasePath = BasePath.substring(0, BasePath.length - 1);
    }

    console.log("Set basepath to " + BasePath);
    DitchClient.basePath = BasePath;
}
else
{
    DitchClient.basePath = '.';
}
