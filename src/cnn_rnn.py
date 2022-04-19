import torch
import torch.nn as nn
from torch.nn.modules.sparse import Embedding
import torchvision.models as models



class EncoderCNN(nn.Module):
    def __init__(self, embed_size, train_CNN=False):
        super(EncoderCNN, self).__init__()
        self.train_CNN = train_CNN

        self.model = models.vgg16(pretrained=False)
        self.first_conv_layer = [nn.Conv2d(1, 3, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=True)]
        self.model.classifier = nn.Linear(25088, embed_size)
        self.first_conv_layer.extend(list(self.model.features))

        # self.inception = models.vgg16(pretrained=False)
        self.model.features= nn.Sequential(*self.first_conv_layer )
        # self.inception.fc = nn.Linear(self.inception.fc.in_features, embed_size)
        # self.first_conv_layer.extend(list(self.inception))
        
        # self.inception.features= nn.Sequential(*self.first_conv_layer ) 


        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, images):
        print(images.shape)
        print(self.model)
        features = self.model(images)
        
        for name, param in self.model.named_parameters():
            if "fc.weight" in name or "fc.bias" in name:
                param.requires_grad = True
            else:
                param.requires_grad = self.train_CNN
        
        return self.dropout(self.relu(features))

class DecoderRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers):
        super(DecoderRNN, self).__init__()
        self.embed = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers)
        self.linear = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(0.5)

    def forward(self, features, caption):
        print(embeddings.shape,features.unsqueeze(0).shape)
        embeddings = torch.cat((features.unsqueeze(0), embeddings), dim=0)
        hiddens, _ = self.lstm(embeddings)
        outputs = self.linear(hiddens)

        return outputs

class CNNtoRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers):
        super(CNNtoRNN, self).__init__()
        self.encoderCNN = EncoderCNN(embed_size)
        self.decoderRNN = DecoderRNN(embed_size, hidden_size, vocab_size, num_layers)
    
    def forward(self, images, captions):
        features = self.encoderCNN(images)
        outputs = self.decoderRNN(features, captions)

        return outputs

    def caption_image(self, image, vocabulary, max_length=50):
        result_caption = []

        with torch.no_grad():
            x = self.encoderCNN(image).unsqueeze(0)
            states = None

            for _ in range(max_length):
                hiddens, states = self.decoderRNN.lstm(x, states)
                output = self.decoderRNN.linear(hiddens.squeeze(0))
                predicted = output.argmax(1)

                result_caption.append(predicted.item())
                x = self.decoderRNN.embed(predicted).unsqueeze(0)

                if vocabulary.itos[predicted.item()] == "<EOS>":
                    break

        return [vocabulary.itos[idx] for idx in result_caption]

if __name__ == "__main__":
    load_model = False
    save_model = False
    train_CNN = False

    # Hyperparameters
    embed_size = 256
    hidden_size = 256
    num_layers = 1
    learning_rate = 3e-4
    num_epochs = 10
    x = torch.randn(1,1,299,256)
    # y = torch.randint(20,1).unsqueeze(0).to(torch.int64)



    voc_size = 1000
    emb_dim = 256
    embedding = nn.Embedding(voc_size, emb_dim)
   

    sentences = torch.randint(high=voc_size, size=(10, 1))
    print(sentences.shape)

    embedded = embedding(sentences)
    print(embedded.shape)

    model = CNNtoRNN(embed_size=embed_size,hidden_size=hidden_size,vocab_size=10000,num_layers=num_layers)
    out = model(x,sentences)