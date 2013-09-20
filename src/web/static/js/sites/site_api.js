var mod = angular.module('siteAjax', [])

mod.factory('SiteApi', function ($http) {


        function patchDeferred(defer) {
            defer.always = function (callback) {
                defer.then(callback,callback);
            }
            return defer
        }


        var saveSite = function saveSite(domain) {
            var defer = $http.post("/rest/save_site", {'domain': domain});

            return patchDeferred(defer)

        }

        return {'saveSite': saveSite}

    }
)
