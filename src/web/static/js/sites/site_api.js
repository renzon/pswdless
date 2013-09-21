var mod = angular.module('siteAjax', [])

mod.factory('SiteApi', function ($http) {


        function patchDeferred(defer) {
            defer.always = function (callback) {
                defer.then(callback, callback);
            }
            return defer;
        }


        return {
            'saveSite': function (domain) {
                var defer = $http.post("/rest/save_site", {'domain': domain});
                return patchDeferred(defer)
            },
            'getSites': function () {
                var defer = $http.post("/rest/get_sites");
                return patchDeferred(defer)
            },
            'updateSite': function (site) {
                var defer = $http.post("/rest/update_site", site);
                return patchDeferred(defer)
            },
            'refreshToken': function (site) {
                var defer = $http.post("/rest/refresh_site_token", site);
                return patchDeferred(defer)
            }
        };

    }
)
