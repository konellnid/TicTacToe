# api/views.py
import datetime

from django.shortcuts import render
from rest_framework.response import Response
from django.http import JsonResponse
from api.serializer import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from api.models import Queue, Game, GameHistory, PlayerAwaiter
from django.db.models import Q
from datetime import datetime
import random

LIST_DIAGONAL_PLACES_FORWARD_SLASH = [2, 4, 6]
LIST_DIAGONAL_PLACES_BACKSLASH = [0, 4, 8]
X_SYMBOL = 'X'
O_SYMBOL = 'O'
X_WON_RESULT = 1
O_WON_RESULT = -1
DRAW_RESULT = 0


# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


def is_move_possible(move_place: int, current_state: str):
    return current_state[move_place] == '_'


def is_move_winning(move_place: int, state: str, symbol: str):
    # check for row win
    row_start = move_place // 3
    if state[row_start] == symbol \
            and state[row_start + 1] == symbol \
            and state[row_start + 2] == symbol:
        return True

    # check for column win
    column_number = move_place % 3
    if state[0 + column_number] == symbol \
            and state[3 + column_number] == symbol \
            and state[6 + column_number] == symbol:
        return True

    # check for diagonal win "\"
    if move_place in LIST_DIAGONAL_PLACES_BACKSLASH \
            and all(state[place] == symbol for place in LIST_DIAGONAL_PLACES_BACKSLASH):
        return True

    # check for diagonal win "/"
    if move_place in LIST_DIAGONAL_PLACES_FORWARD_SLASH \
            and all(state[place] == symbol for place in LIST_DIAGONAL_PLACES_FORWARD_SLASH):
        return True

    return False


def create_game_info_dictionary(game_state: str, is_player_move: bool, is_x_move: bool, is_game_finished: bool,
                                last_move_date: datetime, result=None, is_player_winner=None):
    response_data = {
        'game_state': game_state,
        'is_player_move': is_player_move,
        'is_x_move': is_x_move,
        'is_game_finished': is_game_finished,
        'last_move_date': last_move_date,
        'result': result,
        'is_player_winner': is_player_winner
    }
    return response_data


def create_find_game_info_dictionary(is_player_in_queue: bool, is_player_in_game: bool, description: str):
    response_data = {
        'is_player_in_queue': is_player_in_queue,
        'is_player_in_game': is_player_in_game,
        'description': description
    }
    return response_data


def change_game_state(move_place: int, current_state: str, symbol: str):
    temp_state_list = list(current_state)
    temp_state_list[move_place] = symbol
    return ''.join(temp_state_list)


def end_game(game: Game, end_state: str, was_x_move: bool, result: int):
    game_history_entry = GameHistory(
        x_player=game.x_player,
        o_player=game.o_player,
        end_state=end_state,
        start_date=game.start_date,
        end_date=datetime.now(),
        result=result
    )
    game_history_entry.save()

    waiting_entry_x = PlayerAwaiter(awaiting_player=game.x_player, game_from_history=game_history_entry)
    waiting_entry_o = PlayerAwaiter(awaiting_player=game.o_player, game_from_history=game_history_entry)

    game_history_entry.save()
    waiting_entry_x.save()
    waiting_entry_o.save()
    game.delete()

    return game_history_entry


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_game_end_point(request):
    asking_user = request.user

    # clear awaiting unseen finished games
    PlayerAwaiter.objects.filter(awaiting_player=asking_user).delete()

    if len(Game.objects.filter(Q(o_player=asking_user) | Q(x_player=asking_user))) > 0:
        response_data = create_find_game_info_dictionary(False, True, 'Player already in game.')
        return Response(response_data, status=status.HTTP_200_OK)

    queue = Queue.objects.all()

    if len(queue) == 0:
        new_queue_entity = Queue(waiting_player=asking_user)
        new_queue_entity.save()
        response_data = create_find_game_info_dictionary(True, False, 'Player added to queue.')
        return Response(response_data, status=status.HTTP_200_OK)

    for queue_entity in queue:
        if asking_user.id != queue_entity.waiting_player.id:
            Queue.objects.filter(waiting_player=asking_user).delete()
            Queue.objects.filter(waiting_player=queue_entity.waiting_player).delete()

            players_list = [asking_user, queue_entity.waiting_player]
            random.shuffle(players_list)
            new_game = Game(x_player=players_list[0], o_player=players_list[1])
            new_game.save()

            response_data = create_find_game_info_dictionary(False, True, 'Game created.')
            return Response(response_data, status=status.HTTP_200_OK)

    # only asking player is waiting in queue
    response_data = create_find_game_info_dictionary(True, False, 'Waiting in queue...')
    return Response(response_data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_game(request):
    asking_user = request.user
    user_game = Game.objects.filter(Q(o_player=asking_user) | Q(x_player=asking_user)).first()

    if user_game is None:
        # check if player should be notified about lose
        awaiting_entry = PlayerAwaiter.objects.filter(awaiting_player=asking_user).first()
        if awaiting_entry is None:
            return Response({'response': 'Player is not in game'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = create_game_info_dictionary(awaiting_entry.game_from_history.end_state, False, False, True,
                                                        awaiting_entry.game_from_history.end_date,
                                                        awaiting_entry.game_from_history.result, False)
            return Response(response_data, status=status.HTTP_200_OK)

    is_x_asking = user_game.x_player == asking_user
    is_x_move = user_game.is_x_move
    is_player_move = (is_x_asking and is_x_move) or (not is_x_asking and not is_x_move)

    response_data = create_game_info_dictionary(user_game.current_state, is_player_move, is_x_move, False,
                                                user_game.last_move_date)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_move(request):
    asking_user = request.user
    user_game = Game.objects.filter(Q(o_player=asking_user) | Q(x_player=asking_user)).first()

    if user_game is None:
        return Response({'response': 'Player is not in game'}, status=status.HTTP_400_BAD_REQUEST)

    move_place_string = request.data.get('move_index', '')
    try:
        move_index = int(move_place_string)
    except ValueError:
        return Response({'response': 'Error: move_index_not_int'}, status=status.HTTP_400_BAD_REQUEST)

    if move_index < 0 or move_index > 8:
        return Response({'response': 'Error: wrong number as move index'}, status=status.HTTP_400_BAD_REQUEST)

    is_x_asking = user_game.x_player == asking_user
    is_x_move = user_game.is_x_move
    is_player_move = (is_x_asking and is_x_move) or (not is_x_asking and not is_x_move)

    if not is_player_move:
        return Response({'response': 'Wrong player - not your turn'}, status=status.HTTP_400_BAD_REQUEST)

    if not is_move_possible(move_index, user_game.current_state):
        return Response({'response': 'Move is impossible'}, status=status.HTTP_400_BAD_REQUEST)

    symbol = X_SYMBOL if is_x_move else O_SYMBOL
    updated_state: str = change_game_state(move_index, user_game.current_state, symbol)

    if is_move_winning(move_index, updated_state, symbol):
        # correct, winning move
        result = X_WON_RESULT if is_x_move else O_WON_RESULT
        game_history_entry = end_game(user_game, updated_state, is_x_move, result)
        response_data = create_game_info_dictionary(game_history_entry.end_state, False, False, True,
                                                    game_history_entry.end_date, result, True)

        return Response(response_data, status=status.HTTP_200_OK)
    elif updated_state.__contains__('_'):
        # correct not-winning move, now it's enemy's turn
        user_game.current_state = updated_state
        user_game.last_move_date = datetime.now()
        user_game.is_x_move = not is_x_move
        user_game.save()
        response_data = create_game_info_dictionary(user_game.current_state, False, user_game.is_x_move, False,
                                                    user_game.last_move_date)
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # draw
        game_history_entry = end_game(user_game, updated_state, is_x_move, DRAW_RESULT)
        response_data = create_game_info_dictionary(game_history_entry.end_state, False, False, True,
                                                    game_history_entry.end_date, DRAW_RESULT, False)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def statistics(request):
    statistics_by_id = dict()

    for user in User.objects.all():
        # user_id: [won, drawn, lost]
        statistics_by_id[user.id] = [0, 0, 0]

    for history_game in GameHistory.objects.all():
        if history_game.result == 1:
            statistics_by_id[history_game.x_player_id][0] += 1
            statistics_by_id[history_game.o_player_id][2] += 1
        elif history_game.result == -1:
            statistics_by_id[history_game.x_player_id][2] += 1
            statistics_by_id[history_game.o_player_id][0] += 1
        else:
            statistics_by_id[history_game.x_player_id][1] += 1
            statistics_by_id[history_game.o_player_id][1] += 1

    # change from user_id to username
    statistics_by_username = dict()
    for user in User.objects.all():
        statistics_by_username[user.username] = statistics_by_id[user.id]

    return Response({'statistics': statistics_by_username}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = request.POST.get('text')
        data = f'Congratulation your API just responded to POST request with text: {text}'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status.HTTP_400_BAD_REQUEST)
