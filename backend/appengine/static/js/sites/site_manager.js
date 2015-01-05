var app = angular.module('siteManagerApp', ['siteManager'])

app.config(
    function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{_').endSymbol('_}');
    }
);

function SiteManagerCtrl($scope, SiteApi) {
    $scope.sites = [];
    $scope.loadingSites = true;
    $scope.addSite = function (site) {
        $scope.sites.unshift(site);
    };
    SiteApi.getSites().success(function (sites) {
        $scope.sites = sites;
    }).always(function () {
        $scope.loadingSites = false;
    });

}

var mod = angular.module('siteManager', ['siteAjax']);

mod.directive('domain', function () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            placeholder: '@',
            label: '@',
            errorHeader: '@',
            addSite: '&'
        },
        templateUrl: '/static/js/sites/domain_form.html',
        controller: function ($scope, SiteApi) {
            $scope.domain = '';
            $scope.showAjaxLoader = false;
            $scope.errors = false;
            $scope.saveSite = function () {
                $scope.showAjaxLoader = true;
                $scope.errors = false;
                var obj = SiteApi.saveSite($scope.domain);
                obj.success(function (site) {
                    $scope.domain = '';
                    $scope.addSite({'site': site});
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
});


mod.directive('sitelist', function () {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            idHeader: '@',
            domainHeader: '@',
            tokenHeader: '@',
            saveLabel: '@',
            refreshLabel: '@',
            refreshConfirmation: '@',

            sites: '='
        },
        templateUrl: '/static/js/sites/site_list.html',
        controller: function ($scope, SiteApi) {
            $scope.updateSite = function (site) {
                var postData = {id: site.id, domain: site.domain};
                site.saving = true;
                SiteApi.updateSite(postData).success(function () {
                    site.editing = false;
                }).error(function () {
                    alert("It was not possible changing the site's domain");
                }).always(function () {
                    site.saving = false;
                })

            };
            $scope.editSite = function (site) {
                site.editing = true;
                site.saving = false;
            };

            $scope.refreshToken = function (site) {
                if (confirm($scope.refreshConfirmation)) {
                    site.refreshing = true;
                    var postData = {id: site.id};
                    SiteApi.refreshToken(postData).success(function (result) {
                        site.token = result.token;
                    }).error(function () {
                        alert("It was not possible refreshing site's token now.");
                    }).always(function () {
                        site.refreshing = false;
                    })
                }
            }
        }
    };
});
