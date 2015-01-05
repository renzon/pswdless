var mod = angular.module('siteAjax', [])

mod.factory('SiteApi', function ($rootScope) {
        var createHttpMock = function (returnValue) {
            var httpMock = {
                'success': function (callback) {
                    this.successCallback = callback;
                    return this;
                },
                'error': function (callback) {
                    this.errorCallback = callback;
                    return this;
                },
                'always': function (callback) {
                    this.alwaysCallback = callback;
                    return this;
                }

            }

            function executeAsync() {
                setTimeout(function () {
                    if (httpMock.successCallback !== undefined && returnValue.domain !== '') {
                        httpMock.successCallback(returnValue);
                    }
                    if (httpMock.errorCallback !== undefined && returnValue.domain === '') {
                        httpMock.errorCallback({'errors': {'domain': 'Domain should not be empty'}});
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
        var id = 1;


        return {
            'saveSite': function (domain) {
                id++;
                return createHttpMock({
                    'id': '' + id,
                    'domain': domain,
                    'token': '343jhjhjdfhfd' + id
                });

            },
            'getSites': function () {
                return createHttpMock([
                    {'id': '1', 'domain': 'www.foo.com', 'token': '343jhjhjdfhfd1'}
                ]);
            },
            'updateSite': function e(site) {
                return createHttpMock({'domain': site.domain});
            },
            'refreshToken': function (site) {
                return createHttpMock({'token': 'asdfasdfasdf' + site.id})
            }
        };
    }
)
