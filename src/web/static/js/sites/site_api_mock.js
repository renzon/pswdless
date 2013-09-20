var mod = angular.module('siteAjax', [])

mod.factory('SiteApi', function ($rootScope) {
        var createHttpMock = function (returnValue) {
            var httpMock = {
                'success': function (callback) {
                    this.successCallback = callback;
                    return this;
                },
                'always': function (callback) {
                    this.alwaysCallback = callback;
                    return this;
                }

            }

            function executeAsync() {
                setTimeout(function () {
                    if (httpMock.successCallback !== undefined) {
                        httpMock.successCallback(returnValue);
                    }
                    if (httpMock.alwaysCallback !== null) {
                        httpMock.alwaysCallback(returnValue);
                    }
                    $rootScope.$digest()
                }, 1000);
            }

            executeAsync();
            return httpMock;


        }
        var id = 0;

        var saveSite = function saveSite(domain) {
            id++;
            return createHttpMock({
                'id': ''+id,
                'domain': domain,
                'token': '343jhjhjdfhfd' + id
            })

        }

        return {'saveSite': saveSite}

    }
)
