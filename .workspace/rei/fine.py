from datasets import load_dataset
dataset =load_dataset(
    path="text",
    data_files= {
    "train":"train.txt",
    "test":"test.txt"
    }
)