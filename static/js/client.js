/* global TrelloPowerUp */

var BLACK_ROCKET_ICON = 'https://cdn.glitch.com/1b42d7fe-bda8-4af8-a6c8-eff0cea9e08a%2Frocket-ship.png?1494946700421';
var NEW_USER_ICON = "https://image.flaticon.com/icons/svg/72/72648.svg"
var CHECK_ICON = "https://image.flaticon.com/icons/svg/45/45874.svg"

var trelloKey = "TRELLO-KEY-HERE"
var Promise = TrelloPowerUp.Promise;
var trelloToken;  // cannot get .env variables from client side code, so I need to grab it

var getCurrentList = function (cardID, key, token) {
  var url = `https://api.trello.com/1/cards/${cardID}/list?fields=all&key=${key}&token=${token}`;
  var data = null;
  var xhr = new XMLHttpRequest();
  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === this.DONE) {
      console.log(this.responseText);
    }
  });

  xhr.open("GET", url);
  xhr.send(data);
};

var assignToUserAndStartTesting = function (cardID, memberID, idList, key, token) {
  var url = `https://api.trello.com/1/cards/${cardID}?idMembers=${memberID}&idList=${idList}&pos=top&key=${key}&token=${token}`;
  var data = null;
  var xhr = new XMLHttpRequest();
  xhr.addEventListener("readystatechange", function () {
    if (this.readyState === this.DONE) {
      console.log(this.responseText);
    }
  });

  xhr.open("PUT", url);
  xhr.send(data);
}

window.TrelloPowerUp.initialize({

  'card-buttons': function(t, options) {
    return t.getRestApi().getToken().then(function(token){

      if (token) {

        trelloToken = token
        return [{

          icon: NEW_USER_ICON,
          text: "Begin Testing",
          callback: function(t) {

            return t.popup({

              title: "Start testing?",
              items: [{
                text: "Yes",
                callback: function(t) {

                  var currentContext = t.getContext();
                  var currentBoardID = currentContext.board;
                  var currentCardID = currentContext.card;
                  var currentMemberID = currentContext.member;

                  var targetListID;

                  if (currentBoardID === "5bf329acaf8baf45e81c76e3") {    // test mode
                    targetListID = "5bf329d90ccd194d8ed056cc"
                  } else if (currentBoardID == "5addfe41c66dbead81af5417") {
                    targetListID = "5b7ec18b64a961032fffddf9";
                  };

                  assignToUserAndStartTesting(currentCardID, currentMemberID, targetListID, trelloKey, trelloToken);
                  return t.closePopup();
                },
              }, {
                text: "No",
                callback: function(t) {
                  return t.closePopup();
                }
              }],
            })
          },
          condition: "always"
        }, {
          icon: CHECK_ICON,
          text: "Testing Complete",
          callback: function(t) {
            return t.popup({
              title: "Test Result?",
              items: [{
                text: "Pass",
                callback: function(t) {

                  var currentContext = t.getContext();
                  var currentBoardID = currentContext.board;
                  var currentCardID = currentContext.card;
                  var currentMemberID = currentContext.member;

                  var targetListID;

                  if (currentBoardID === "5bf329acaf8baf45e81c76e3") {    // test mode
                    targetListID = "5bfc71886a938d8f06f1de14"
                  } else if (currentBoardID == "5addfe41c66dbead81af5417") {
                    targetListID = "5addfe8f62a68b9ac9565f90";
                  };

                  assignToUserAndStartTesting(currentCardID, currentMemberID, targetListID, trelloKey, trelloToken);
                  return t.closePopup();
                },
              }, {
                text: "Fail",
                callback: function(t) {

                  var currentContext = t.getContext();
                  var currentBoardID = currentContext.board;
                  var currentCardID = currentContext.card;
                  var currentMemberID = currentContext.member;

                  var targetListID;

                  if (currentBoardID === "5bf329acaf8baf45e81c76e3") {    // test mode
                    targetListID = "5bf329d26d39761f59a29ffc"
                  } else if (currentBoardID == "5addfe41c66dbead81af5417") {
                    targetListID = "5b23cea20c7cdab6de54398c";
                  };

                  assignToUserAndStartTesting(currentCardID, currentMemberID, targetListID, trelloKey, trelloToken);
                  return t.closePopup();
                }
              }],
            })
          },
          condition: 'always'
        }]
      } else {
        window.Trello.authorize({
          type: 'popup',
          name: 'App Name',
          scope: {
            read: 'true',
            write: 'true' },
          expiration: 'never',
          success: function(){console.log("Success!");},
          error: function(){console.log("Failure!");},
        });
      }
    })
  }
}, {
  appName: "App Name",
  appKey: "APP-KEY-HERE"
});
