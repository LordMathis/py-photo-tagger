from tagger import utils
from tagger.model.model_register import ModelRegister
from tagger.worker import Worker

model_register = ModelRegister()
model_register.find_all_models()

json_data = None
try:
    json_data = utils.read_json_file('./taggs.json')
except OSError:
    pass

workers = []
for model_handler in model_register.list_models():
    worker = Worker(model_handler, json_data)
    worker.start()
    workers.append(worker)

for worker in workers:
    worker.join()

# if __name__ == '__main__':
#     app.run(debug=True)
