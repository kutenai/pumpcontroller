/**
 * Copyright: Aspen Labs, LLC. 2011
 * User: kutenai
 * Date: 5/23/13
 * Time: 6:48 PM
 */

var ditchModule = angular.module('ditchApp', ['ngResource',]);

ditchModule.factory('DitchService', function($http) {

    return {
        start: function(zone) {
            $http.post('/ctrl/', { zone: zone });
        },
        stop: function(zone) {
            $http.delete('/ctrl/');
        }

    };
});

ditchModule.factory('DitchControl', ['$resource', function($resource) {
    return $resource('/ctrl/',{},
        {
            getData: {
                method:'GET'
            }
        }
    )
}]);

ditchModule.controller('DitchController', function ($scope,$timeout,$resource,DitchService) {

    $scope.dc = $resource(
        '/ctrl',
        {},
        {
            info: {
                method: "GET"
            }
        }
    );
    console.log("Get Info\n");
    $scope.dc.info(function(data) {
        $scope.info = data;
    });
    //var info = $scope.ctrl.get();
    console.log("Yeah\n!");

    $scope.info = {
        'ditch_inches' : 10.12,
        'sump_inches' : 18.1,
        'pump_on' : 0,
        'north_on' : 0,
        'south_on' : 0
    };

    $scope.ditchStart = function(zone) {
        console.log("Starting zone " + zone);
        if (zone === 'north') {
            DitchService.start('north');
        } else if (zone === 'south') {
            DitchService.start('south');
        }
    }
    $scope.ditchStop = function() {
        console.log("Stopping the ditch.");
        DitchService.stop();
    }

    $scope.onTimeout = function(){
        $scope.dc.info(function(data) {
            $scope.info.ditch_inches = parseFloat(data.ditch_in);
            $scope.info.sump_inches = parseFloat(data.sump_in);
            $scope.info.pump_on = data.pumpon;
            $scope.info.north_on = data.northon;
            $scope.info.south_on = data.southon;
        });

        //$scope.info = $scope.ctrl.query();
        mytimeout = $timeout($scope.onTimeout,1000);
    }
    var mytimeout = $timeout($scope.onTimeout,1000);

});


