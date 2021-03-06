# ──────────────────────────────────────────────────────────────────────────────
# The Cards controller handle the cards visualization mode behaviors
# ──────────────────────────────────────────────────────────────────────────────
class CardsCtrl


    @$inject: ['$scope', '$translate', 'searchService', 'shareService']

    constructor: (@scope, @$translate, @searchService, Share, @Page) ->
        # inherited method from TabsCtrl
        @scope.setTitle(@$translate('SEARCH_CARDS_TAB_HEADING'))
        # ──────────────────────────────────────────────────────────────────────
        # scope variables function binding
        # ──────────────────────────────────────────────────────────────────────
        # Variables
        @scope.onlyRelevantCards = true

        # Functions
        @scope.search = @searchService
        @scope.showDetails = @showDetails
        @scope.showSharing = @showSharing
        @scope.cardsFilter = @filterCards
        @scope.loadMore = @loadMore
        # For sharing purpose
        @scope.sharingAddress = (d) ->
            Share.getSharingAddress d.title, 'cards'
        @scope.embedFrame = (d) ->
            Share.getEmbedFrame d.title

        @scope.setLoading no

    showDetails: (d)=>
        # show a card detail
        d.show = if d.show is 'infos' then 'preview' else 'infos'

    showSharing: (d)=>
        d.show = if d.show is 'sharing' then 'preview' else 'sharing'

    filterCards: (c)=>
        return false unless c? and _.isObject(c)
        if @scope.onlyRelevantCards
            return c.relevance_score > 6
        return true


    loadMore:()=>
        @scope.onlyRelevantCards = false


angular.module('stories').controller 'cardsCtrl', CardsCtrl