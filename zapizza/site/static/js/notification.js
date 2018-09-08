"use strict"
/*  base: https://github.com/mouse0270/bootstrap-notify
    params:
    titulo: primeira palavra do alerta
    mensagem: texto do corpo da mensagem
    url: direciona para url ao clicar na mensagem
    target: modo de abertura da url (_blank | _self | _parent | _top)

    methods:
    alert_primary('mensagem mensagem mensagem');
    alert_success('mensagem mensagem mensagem');
    alert_danger('mensagem mensagem mensagem');
    alert_warning('mensagem mensagem mensagem');
*/
function alert_primary(mensagem) {
$.notify({
	icon: 'fa fa-info',
	title: null,
	message: mensagem,
	url: null,
	target: null
},{
	element: 'body',
	position: null,
	type: "primary",
	allow_dismiss: true,
	newest_on_top: false,
	showProgressbar: false,
	placement: {
		from: "top",
		align: "center"
	},
	offset: 20,
	spacing: 10,
	z_index: 1031,
	delay: 2000,
	timer: 2000,
	url_target: '_blank',
	mouse_over: null,
	animate: {
		enter: 'animated fadeInDown',
		exit: 'animated fadeOutUp'
	},
	icon_type: 'class'
});
}

function alert_success(mensagem) {
$.notify({
	icon: 'fa fa-check',
	title: null,
	message: mensagem,
	url: null,
	target: null
},{
	element: 'body',
	position: null,
	type: "success",
	allow_dismiss: true,
	newest_on_top: false,
	showProgressbar: false,
	placement: {
		from: "top",
		align: "center"
	},
	offset: 20,
	spacing: 10,
	z_index: 1031,
	delay: 2000,
	timer: 5000,
	url_target: '_blank',
	mouse_over: null,
	animate: {
		enter: 'animated fadeInDown',
		exit: 'animated fadeOutUp'
	},
	icon_type: 'class'
});
}

function alert_danger(mensagem) {
$.notify({
	icon: 'fa fa-ban',
	title: null,
	message: mensagem,
	url: null,
	target: null
},{
	element: 'body',
	position: null,
	type: "danger",
	allow_dismiss: true,
	newest_on_top: false,
	showProgressbar: false,
	placement: {
		from: "top",
		align: "center"
	},
	offset: 20,
	spacing: 10,
	z_index: 1031,
	delay: 2000,
	timer: 10000,
	url_target: '_blank',
	mouse_over: null,
	animate: {
		enter: 'animated fadeInDown',
		exit: 'animated fadeOutUp'
	},
	icon_type: 'class'
});
}

function alert_warning(mensagem) {
$.notify({
	icon: 'fa fa-exclamation',
	title: null,
	message: mensagem,
	url: null,
	target: null
},{
	element: 'body',
	position: null,
	type: "warning",
	allow_dismiss: true,
	newest_on_top: false,
	showProgressbar: false,
	placement: {
		from: "top",
		align: "center"
	},
	offset: 20,
	spacing: 10,
	z_index: 1031,
	delay: 2000,
	timer: 5000,
	url_target: '_blank',
	mouse_over: null,
	animate: {
		enter: 'animated fadeInDown',
		exit: 'animated fadeOutUp'
	},
	icon_type: 'class'
});
}