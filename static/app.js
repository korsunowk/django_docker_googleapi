var emailApp = angular.module('emailApp', []);

emailApp.factory('emailFactory', function($http) {
	var factory = {};

	factory.getEmailList = function() {
		return $http.get('/get_emails');
	};

	return factory;
});


emailApp.controller('emailController', function($scope, emailFactory) {
	var email = this;

	email.emailList = [];
	emailFactory.getEmailList().success(function(data) {
		email.emailList = data.messages;
	});

	email.Refresh = function() {

		emailFactory.getEmailList().success(function(data) {
			email.emailList = data.messages;
		});
	}
});

emailApp.directive('emailItem', function() {
	return  {
		restrict: 'E',
		scope: {
			email: '=email'
		},
		template: '<div><h1>{{ email.From }}</h1><h1>{{ email.To }}</h1><h2>{{ email.Subject }}</h2><p>{{ email.Message }}</p><h6>{{ email.Date }}</h6></div><hr>'
	};
});