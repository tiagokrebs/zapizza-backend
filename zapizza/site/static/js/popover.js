"use strict";
/* base: https://getbootstrap.com/docs/4.0/components/popovers/
*/
    $(function () {
          $('[data-toggle="popover"]').popover({
          trigger: 'hover',
          placement: 'top',
          fallbackPlacement: 'flip'
          })
    })