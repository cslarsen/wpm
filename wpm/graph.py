import pandas as pd
import gnuplotlib as gp


df = pd.read_csv('~/.wpm.csv')
df.columns = ['race', 'wpm', 'Accuracy', 'Rank', 'Racers', 'text_id', 'Timestamp', 'Database', 'Keyboard']

wpm = df['wpm']
print wpm

gp.plot( (wpm, {'legend': 'WPM'}),

         title='WPM Graph',
         _with='lines lc rgb "red"',
         terminal='dumb 80,40',
         unset='grid')
