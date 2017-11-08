var myApp = angular.module('tabApp', []);

myApp.controller('TabController', function ($scope, $http, $timeout) {
    $scope.smsg = "";
    $scope.cdt = "";
    $scope.ctm = "";
    $scope.fdt = "";
    $scope.tdt = "";
    $scope.entries = [];
    $scope.tab = 0;
    $scope.indx = 0;
    $scope.sindx = -1;
    $scope.ent_len = 0;
    $scope.currentries = [];
    $scope.sldno1 = "";
    $scope.sldno2 = "";
    $scope.sldno3 = "";
    $scope.mtype = "";
    $scope.imnm = "";

    $scope.refreshnbmsg = function (){
        $scope.serverop('get_nb');
    }

	$scope.getnbmsg = function () {
	    $scope.mytimeout = $timeout($scope.refreshnbmsg, 10000);
	}

	$scope.refreshdt = function (){
        $scope.serverop('get_cdt');
    }

	$scope.getcdt = function () {
	    $scope.mytimeout1 = $timeout($scope.refreshdt, 1000);
	}

    $scope.serverop = function(starget) {
        try {
            var responsePromise = $http.get(starget);
        }
        catch(err) {
            $scope.smsg = "There is some error in python apis, Please contact administrator!";
        }
        responsePromise.success(function(response, status, headers, config){
            var resp = response;
            var typ=resp.starg;

            if(typ=="get_nb")
            {
                var frdt = response.fdt;
                var todt = response.tdt;
                $scope.entries = response.entries;
                $scope.ent_len = $scope.entries.length;
                $scope.mtype = response.mtype;

                if(!$scope.entries || !$scope.entries.length)
                {
                    $scope.tab = 1;

                    $scope.sindx++;
                    if($scope.sindx == 4)
                    {
                        $scope.sindx = 0;
                    }
                    if($scope.sindx == 0)
                    {
                        $scope.sldno1 = "item active";
                        $scope.sldno2 = "item";
                        $scope.sldno3 = "item";
                    }
                    else if($scope.sindx == 1)
                    {
                        $scope.sldno1 = "item";
                        $scope.sldno2 = "item active";
                        $scope.sldno3 = "item";
                    }
                    else if($scope.sindx == 2)
                    {
                        $scope.sldno1 = "item";
                        $scope.sldno2 = "item";
                        $scope.sldno3 = "item active";
                    }
                }
                else
                {
                    $scope.tab = 0;
                    if(($scope.fdt != frdt) || ($scope.tdt != todt))
                    {
                        $scope.fdt = frdt;
                        $scope.tdt = todt;
                        $scope.currentries = response.currentries;
                        $scope.indx = 0;
                    }
                    else
                    {
                        $scope.indx++;
                        if($scope.indx == $scope.ent_len)
                        {
                            $scope.indx = 0;
                        }
                        console.log($scope.indx);
                        $scope.currentries = [];
                        $scope.currentries.push($scope.entries[$scope.indx]);
                    }
                    $scope.imnm = "static/nbdimg/"+$scope.entries[$scope.indx]['nbid'] +".jpg";
                    console.log($scope.imnm);
                }

                $timeout.cancel($scope.mytimeout);
                $scope.getnbmsg();
            }
            else if(typ=="get_cdt")
            {
                $scope.cdt = response.cdt;
                $scope.ctm = response.ctm;
                $timeout.cancel($scope.mytimeout1);
                $scope.getcdt();
            }
        });

        responsePromise.error(function(err, status, headers, config){
            console.log(err);
        });
    }


});
