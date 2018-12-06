Forked from: https://github.com/abisee/cnn-dailymail

This code provides several methods of processing input files of various types into the binary format expected by the [code](https://github.com/abisee/pointer-generator) for the Tensorflow model.

This code has been adapted into Python 3 and modified in other ways by Leah Hamilton from [@abisee's code for processing the CNN/Daily Mail dataset](https://github.com/abisee/cnn-dailymail) and [@chmillee's fork](https://github.com/chmille3/process_data_for_pointer_summrizer).

## 1. Starting data formats
You can use:
A .json file with a single .json object per cluster, as described in the report as clusters.json (json_to_story.py)
A single text file with one document per line (txt_to_story.py)
A directory fo text files with one document each (txts_to_story.py)

## 2. Download Stanford CoreNLP
We will need Stanford CoreNLP to tokenize the data. Download it [here](https://stanfordnlp.github.io/CoreNLP/) and unzip it. Then add the following command to your bash_profile:
```
export CLASSPATH=/path/to/stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0.jar
```
replacing `/path/to/` with the path to where you saved the `stanford-corenlp-full-2016-10-31` directory. You can check if it's working by running
```
echo "Please tokenize this text." | java edu.stanford.nlp.process.PTBTokenizer
```
You should see something like:
```
Please
tokenize
this
text
.
PTBTokenizer tokenized 5 tokens at 68.97 tokens per second.
```
## 3. Process into .bin and vocab files
The run process is in two parts.

Part 1, run one of
```
python json_to_story.py -f <file name> -o <output directory> -s <folder name for story files>
python txts_to_story.py -f <input directory> -o <output directory> -s <folder name for story files>
python txt_to_story.py -f <input text file> -o <output directory> -s <folder name for story files>
```

The JSON file (-f) must have tags “originalurl”, “clusterid”, and article body “text”.
“originalurl” and “text” are assumed to be arrays in the same order, one per cluster.
For each URL, a unique hash is made from the URL.
In txt-processing formats, the original filename is hashed instead
For the respective article, makes a file: <hash>.story
These .story files are written to the output directory (-o/-s).
All the URLs or filenames (whichever was hashed) are written to the file: all_urls.txt, one per line.
all_urls.txt is saved to -o

Part 2, run

```
python make_datafiles.py -m <mode: train.bin, test.bin, or val.bin> -s <folder containing story files> -w <working directory>
```
NOTE`<output dir>` from part 1 should be passed to `-w`.
-s is optional if the subdirectory with the story files -s from part 1 is default `story_files`

This takes in a directory -w\-s which contains the articles in <hash>.story format and creates a .bin with the provided name: train.bin, test.bin, or val.bin.
Tokenized stories are written to the directory: -w\`tokenized_stories`.
NOTE: If the tokenized_stories directory exists, it must be empty before running this command!

Additionally a `vocab` file is created from the training data. This is also placed in -w\`finished_files`. NOTE: If you are using the pretrained model linked from [here](https://github.com/chmille3/pointer-generator), use the vocab file provided with this project.


Lastly, <story type: train.bin, test.bin, or val.bin> will be split into chunks of 1000 examples per chunk. These chunked files will be saved in `finished_files/chunked` as e.g. `train_000.bin`, `train_001.bin`, ..., `train_287.bin`. This should take a few seconds. You can use either the single files or the chunked files as input to the Tensorflow code (see considerations [here](https://github.com/abisee/cnn-dailymail/issues/3)).
