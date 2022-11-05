from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


# Create your models here.
class Game(models.Model):
    x_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_x')
    o_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_o')

    current_state = models.CharField(default='_________', max_length=9)
    is_x_move = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=datetime.now)
    last_move_date = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.x_player_id} vs {self.o_player_id}: {self.current_state}'


class GameHistory(models.Model):
    x_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_games_as_x')
    o_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_games_as_o')

    end_state = models.CharField(max_length=9)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default=datetime.now)
    result = models.IntegerField()

    def __str__(self):
        return f'{self.x_player_id} vs {self.o_player_id}: {self.end_state}'


class Queue(models.Model):
    waiting_player = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.waiting_player_id}'


class PlayerAwaiter(models.Model):
    awaiting_player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_from_history = models.ForeignKey(GameHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.awaiting_player_id}, {self.game_from_history_id}'
