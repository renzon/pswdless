var mod = angular.module('siteManager', ['siteAjax'])

mod.directive('domain', function () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            placeholder: '@',
            label: '@',
            errorHeader: '@'
        },
        templateUrl: '/static/js/sites/domain_form.html',
        controller: function ($scope, SiteApi) {
            $scope.domain = '';
            $scope.showAjaxLoader = false;
            $scope.errors = false;
            $scope.saveSite = function () {
                $scope.showAjaxLoader = true;
                $scope.errors = false;
                var obj = SiteApi.saveSite($scope.domain)
                obj.success(function (site) {
                }).error(function (data) {
                        if (data.hasOwnProperty('errors')) {
                            $scope.errors = data.errors
                        }
                    }).always(function () {
                        $scope.showAjaxLoader = false;
                    })
            }

        }
    };
})
