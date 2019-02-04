#%% [markdown]
# Copyright (c) Microsoft Corporation. All rights reserved.
# 
# Licensed under the MIT License.
#%% [markdown]
# ## Configure your Azure ML workspace
# 
# ### Workspace parameters
# 
# To use an AML Workspace, you will need to import the Azure ML SDK and supply the following information:
# * Your subscription id
# * A resource group name
# * (optional) The region that will host your workspace
# * A name for your workspace
# 
# You can get your subscription ID from the [Azure portal](https://portal.azure.com).
# 
# You will also need access to a [_resource group_](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-overview#resource-groups), which organizes Azure resources and provides a default region for the resources in a group.  You can see what resource groups to which you have access, or create a new one in the [Azure portal](https://portal.azure.com).  If you don't have a resource group, the create workspace command will create one for you using the name you provide.
# 
# The region to host your workspace will be used if you are creating a new workspace.  You do not need to specify this if you are using an existing workspace. You can find the list of supported regions [here](https://azure.microsoft.com/en-us/global-infrastructure/services/?products=machine-learning-service).  You should pick a region that is close to your location or that contains your data.
# 
# The name for your workspace is unique within the subscription and should be descriptive enough to discern among other AML Workspaces.  The subscription may be used only by you, or it may be used by your department or your entire enterprise, so choose a name that makes sense for your situation.
# 
# The following cell allows you to specify your workspace parameters.  This cell uses the python method `os.getenv` to read values from environment variables which is useful for automation.  If no environment variable exists, the parameters will be set to the specified default values.  
# 
# If you ran the Azure Machine Learning [quickstart](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started) in Azure Notebooks, you already have a configured workspace!  You can go to your Azure Machine Learning Getting Started library, view *config.json* file, and copy-paste the values for subscription ID, resource group and workspace name below.
# 
# Replace the default values in the cell below with your workspace parameters

#%%
from azureml.core import Workspace

subscription_id = "<my-subscription-id>"
resource_group = "<my-resource-group>"
workspace_name = "<my-workspace-name>"

# supported regions: https://azure.microsoft.com/en-us/global-infrastructure/services/?products=machine-learning-service
workspace_region = "eastus2" 


#%%
# Create a new workspace if it doesn't exist

ws = Workspace.create(name = workspace_name,
                      subscription_id = subscription_id,
                      resource_group = resource_group, 
                      location = workspace_region,
                      create_resource_group = True,
                      exist_ok = True)

print('workspace details:')
print(ws.get_details())


#%%
# Get the workspace and write a workspace configuration file

try:
    ws = Workspace(subscription_id = subscription_id, resource_group = resource_group, workspace_name = workspace_name)
    ws.write_config()
    print("Write Workspace configuration file succeeded.")
except:
    print("Fail to write Workspace configuration file.")


