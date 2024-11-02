import json
import hcl2
import yaml
from typing import Dict, Any, Union, List, Optional
import re

class CloudFormatConverter:
    def __init__(self):
        # Expanded resource type mappings
        self.resource_type_mappings = {
            # Compute
            "AWS::EC2::Instance": "aws_instance",
            "AWS::EC2::Volume": "aws_ebs_volume",
            "AWS::EC2::VPC": "aws_vpc",
            "AWS::EC2::Subnet": "aws_subnet",
            "AWS::EC2::SecurityGroup": "aws_security_group",
            "AWS::EC2::RouteTable": "aws_route_table",
            "AWS::EC2::NetworkInterface": "aws_network_interface",
            
            # Storage
            "AWS::S3::Bucket": "aws_s3_bucket",
            "AWS::S3::BucketPolicy": "aws_s3_bucket_policy",
            "AWS::EFS::FileSystem": "aws_efs_file_system",
            
            # Database
            "AWS::RDS::DBInstance": "aws_db_instance",
            "AWS::RDS::DBCluster": "aws_rds_cluster",
            "AWS::DynamoDB::Table": "aws_dynamodb_table",
            
            # Networking
            "AWS::ElasticLoadBalancingV2::LoadBalancer": "aws_lb",
            "AWS::ElasticLoadBalancingV2::TargetGroup": "aws_lb_target_group",
            "AWS::ElasticLoadBalancingV2::Listener": "aws_lb_listener",
            
            # Identity
            "AWS::IAM::Role": "aws_iam_role",
            "AWS::IAM::Policy": "aws_iam_policy",
            "AWS::IAM::User": "aws_iam_user",
            "AWS::IAM::Group": "aws_iam_group",
            
            # Serverless
            "AWS::Lambda::Function": "aws_lambda_function",
            "AWS::ApiGateway::RestApi": "aws_api_gateway_rest_api",
            "AWS::ApiGateway::Resource": "aws_api_gateway_resource",
            "AWS::ApiGateway::Method": "aws_api_gateway_method",
            
            # Containers
            "AWS::ECS::Cluster": "aws_ecs_cluster",
            "AWS::ECS::Service": "aws_ecs_service",
            "AWS::ECS::TaskDefinition": "aws_ecs_task_definition",
            
            # Monitoring
            "AWS::CloudWatch::Alarm": "aws_cloudwatch_metric_alarm",
            "AWS::CloudWatch::Dashboard": "aws_cloudwatch_dashboard",
            "AWS::SNS::Topic": "aws_sns_topic"
        }
        
        # Reverse mappings for terraform to cloudformation
        self.reverse_resource_type_mappings = {
            v: k for k, v in self.resource_type_mappings.items()
        }
        
        # Function mappings for intrinsic functions
        self.cf_to_tf_functions = {
            "Fn::Join": self._convert_join,
            "Fn::Sub": self._convert_sub,
            "Ref": self._convert_ref,
            "Fn::GetAtt": self._convert_get_att,
            "Fn::Select": self._convert_select,
            "Condition": self._convert_condition
        }
        
        self.tf_to_cf_functions = {
            "join": self._convert_to_cf_join,
            "format": self._convert_to_cf_sub,
            "aws_region": {"Ref": "AWS::Region"},
            "aws_account_id": {"Ref": "AWS::AccountId"}
        }

    def tf_to_cf(self, tf_content: str) -> Dict[str, Any]:
        """Convert Terraform HCL to CloudFormation template"""
        try:
            # Parse HCL content
            tf_dict = hcl2.loads(tf_content)
            
            # Initialize CloudFormation template structure
            cf_template = {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Description": "Converted from Terraform",
                "Parameters": {},
                "Conditions": {},
                "Resources": {},
                "Outputs": {}
            }
            
            # Convert variables to parameters
            if "variable" in tf_dict:
                cf_template["Parameters"].update(
                    self._convert_variables_to_parameters(tf_dict["variable"])
                )
            
            # Convert resources
            if "resource" in tf_dict:
                cf_template["Resources"].update(
                    self._convert_tf_resources_to_cf(tf_dict["resource"])
                )
            
            # Convert outputs
            if "output" in tf_dict:
                cf_template["Outputs"].update(
                    self._convert_tf_outputs_to_cf(tf_dict["output"])
                )
            
            # Convert provider configurations
            if "provider" in tf_dict:
                self._handle_provider_config(tf_dict["provider"], cf_template)
            
            # Remove empty sections
            cf_template = {k: v for k, v in cf_template.items() if v}
            
            return cf_template
        
        except Exception as e:
            raise Exception(f"Error converting Terraform to CloudFormation: {str(e)}")

    def cf_to_tf(self, cf_content: Union[str, Dict]) -> str:
        """Convert CloudFormation template to Terraform HCL"""
        try:
            # Parse CloudFormation template if it's a string
            if isinstance(cf_content, str):
                if cf_content.startswith('{'):
                    cf_dict = json.loads(cf_content)
                else:
                    cf_dict = yaml.safe_load(cf_content)
            else:
                cf_dict = cf_content
            
            # Initialize Terraform configuration
            tf_config = {
                "terraform": {
                    "required_providers": {
                        "aws": {
                            "source": "hashicorp/aws",
                            "version": "~> 4.0"
                        }
                    }
                },
                "provider": {
                    "aws": self._extract_provider_config(cf_dict)
                },
                "variable": self._convert_parameters_to_variables(cf_dict.get("Parameters", {})),
                "resource": {},
                "output": self._convert_cf_outputs_to_tf(cf_dict.get("Outputs", {}))
            }
            
            # Convert resources
            tf_config["resource"] = self._convert_cf_resources_to_tf(cf_dict.get("Resources", {}))
            
            # Remove empty sections
            tf_config = {k: v for k, v in tf_config.items() if v}
            
            return self._format_tf_output(tf_config)
        
        except Exception as e:
            raise Exception(f"Error converting CloudFormation to Terraform: {str(e)}")

    def _convert_variables_to_parameters(self, variables: Dict) -> Dict:
        """Convert Terraform variables to CloudFormation parameters"""
        parameters = {}
        
        for var_name, var_config in variables.items():
            parameter = {
                "Type": self._get_cf_parameter_type(var_config.get("type", "string")),
                "Description": var_config.get("description", f"Parameter for {var_name}")
            }
            
            if "default" in var_config:
                parameter["Default"] = var_config["default"]
            
            if "validation" in var_config:
                if "condition" in var_config["validation"]:
                    parameter["AllowedPattern"] = var_config["validation"]["condition"]
                
                if "allowed_values" in var_config["validation"]:
                    parameter["AllowedValues"] = var_config["validation"]["allowed_values"]
            
            parameters[var_name] = parameter
        
        return parameters

    def _convert_parameters_to_variables(self, parameters: Dict) -> Dict:
        """Convert CloudFormation parameters to Terraform variables"""
        variables = {}
        
        for param_name, param_config in parameters.items():
            variable = {
                "type": self._get_tf_variable_type(param_config["Type"]),
                "description": param_config.get("Description", f"Variable for {param_name}")
            }
            
            if "Default" in param_config:
                variable["default"] = param_config["Default"]
            
            if "AllowedValues" in param_config:
                variable["validation"] = {
                    "condition": f"can(index([{', '.join(map(repr, param_config['AllowedValues']))}], var.{param_name}))",
                    "error_message": f"Variable {param_name} must be one of: {', '.join(map(str, param_config['AllowedValues']))}"
                }
            
            variables[param_name] = variable
        
        return variables

    def _convert_tf_resources_to_cf(self, resources: Dict) -> Dict:
        """Convert Terraform resources to CloudFormation resources"""
        cf_resources = {}
        
        for resource_type, type_resources in resources.items():
            for resource_name, resource_config in type_resources.items():
                cf_resource_type = self.reverse_resource_type_mappings.get(
                    resource_type,
                    f"AWS::{resource_type.split('_')[1].title()}::{resource_type.split('_')[2].title()}"
                )
                
                # Handle dependencies
                depends_on = resource_config.pop("depends_on", [])
                
                # Convert the resource configuration
                cf_resources[resource_name] = {
                    "Type": cf_resource_type,
                    "Properties": self._convert_tf_properties_to_cf(resource_config)
                }
                
                # Add DependsOn if needed
                if depends_on:
                    cf_resources[resource_name]["DependsOn"] = depends_on
        
        return cf_resources

    def _convert_cf_resources_to_tf(self, resources: Dict) -> Dict:
        """Convert CloudFormation resources to Terraform resources"""
        tf_resources = {}
        
        for resource_name, resource_data in resources.items():
            cf_type = resource_data["Type"]
            tf_type = self.resource_type_mappings.get(
                cf_type,
                f"aws_{cf_type.split('::')[1].lower()}_{cf_type.split('::')[2].lower()}"
            )
            
            # Initialize resource type if not exists
            if tf_type not in tf_resources:
                tf_resources[tf_type] = {}
            
            # Convert properties
            resource_config = self._convert_cf_properties_to_tf(
                resource_data.get("Properties", {})
            )
            
            # Handle dependencies
            if "DependsOn" in resource_data:
                resource_config["depends_on"] = (
                    [resource_data["DependsOn"]]
                    if isinstance(resource_data["DependsOn"], str)
                    else resource_data["DependsOn"]
                )
            
            tf_resources[tf_type][resource_name] = resource_config
        
        return tf_resources

    def _convert_tf_outputs_to_cf(self, outputs: Dict) -> Dict:
        """Convert Terraform outputs to CloudFormation outputs"""
        cf_outputs = {}
        
        for output_name, output_config in outputs.items():
            cf_output = {
                "Description": output_config.get("description", f"Output {output_name}"),
                "Value": self._convert_tf_value_to_cf(output_config["value"])
            }
            
            if output_config.get("sensitive", False):
                cf_output["NoEcho"] = True
            
            cf_outputs[output_name] = cf_output
        
        return cf_outputs

    def _convert_cf_outputs_to_tf(self, outputs: Dict) -> Dict:
        """Convert CloudFormation outputs to Terraform outputs"""
        tf_outputs = {}
        
        for output_name, output_config in outputs.items():
            tf_output = {
                "description": output_config.get("Description", f"Output {output_name}"),
                "value": self._convert_cf_value_to_tf(output_config["Value"])
            }
            
            if output_config.get("NoEcho", False):
                tf_output["sensitive"] = True
            
            tf_outputs[output_name] = tf_output
        
        return tf_outputs

    def _convert_join(self, params: List) -> str:
        """Convert Fn::Join to Terraform format"""
        delimiter, items = params
        return f"${{join('{delimiter}', {json.dumps(items)})}}"

    def _convert_sub(self, params: Union[str, List]) -> str:
        """Convert Fn::Sub to Terraform format"""
        if isinstance(params, str):
            # Simple substitution
            return self._convert_simple_sub(params)
        else:
            # Complex substitution with mapping
            template, mapping = params
            return self._convert_complex_sub(template, mapping)

    def _convert_ref(self, ref_name: str) -> str:
        """Convert Ref to Terraform format"""
        if ref_name.startswith("AWS::"):
            # Handle AWS pseudo parameters
            pseudo_params = {
                "AWS::Region": "data.aws_region.current.name",
                "AWS::AccountId": "data.aws_caller_identity.current.account_id",
                "AWS::StackName": "terraform.workspace"
            }
            return f"${{${pseudo_params.get(ref_name, ref_name)}}}"
        else:
            # Regular reference
            return f"${{var.{ref_name}}}"

    def _convert_get_att(self, params: List) -> str:
        """Convert Fn::GetAtt to Terraform format"""
        resource_name, attribute = params
        return f"${{aws_{resource_name.lower()}.{attribute.lower()}}}"

    def _convert_select(self, params: List) -> str:
        """Convert Fn::Select to Terraform format"""
        index, array = params
        return f"${{element({json.dumps(array)}, {index})}}"

    def _convert_condition(self, condition_name: str) -> str:
        """Convert Condition to Terraform format"""
        return f"${{var.{condition_name}}}"

    def _convert_to_cf_join(self, tf_expression: str) -> Dict:
        """Convert Terraform join to Fn::Join"""
        # Extract delimiter and items from join("delimiter", [...])
        match = re.match(r'join\("([^"]+)",\s*\[(.*)\]\)', tf_expression)
        if match:
            delimiter, items = match.groups()
            return {"Fn::Join": [delimiter, json.loads(f"[{items}]")]}
        return tf_expression

    def _convert_to_cf_sub(self, tf_expression: str) -> Dict:
        """Convert Terraform string interpolation to Fn::Sub"""
        # Convert ${var.name} to ${Name} format
        template = re.sub(r'\$\{var\.([^}]+)\}', r'${{\1}}', tf_expression)
        return {"Fn::Sub": template}

    def _get_cf_parameter_type(self, tf_type: str) -> str:
        """Map Terraform variable types to CloudFormation parameter types"""
        type_mapping = {
            "string": "String",
            "number": "Number",
            "bool": "String",
            "list": "CommaDelimitedList",
            # Complex types
            "map": "String",
            "object": "String",
            "set": "CommaDelimitedList"
        }
        return type_mapping.get(tf_type, "String")

    def _get_tf_variable_type(self, cf_type: str) -> str:
        """Map CloudFormation parameter types to Terraform variable types"""
        type_mapping = {
            "String": "string",
            "Number": "number",
            "CommaDelimitedList": "list(string)",
            "List<Number>": "list(number)",
            "AWS::EC2::KeyPair::KeyName": "string",
            "AWS::EC2::SecurityGroup::Id": "string",
            "AWS::EC2::Subnet::Id": "string",
            "AWS::EC2::VPC::Id": "string"
        }
        return type_mapping.get(cf_type, "string")

    def _handle_provider_config(self, provider_config: Dict, cf_template: Dict) -> None:
        """Handle Terraform provider configuration"""
        if "aws" in provider_config:
            aws_config = provider_config["aws"]
            
            # Handle region
            if "region" in aws_config:
                cf_template["Mappings"] = cf_template.get("Mappings", {})
                cf_template["Mappings"]["AWSRegionMap"] = {
                    "Region": {"Name": aws_config["region"]}
                }
            
            # Handle assumed role
            if "assume_role" in aws_config:
                role_arn = aws_config["assume_role"].get("role_arn")
                if role_arn:
                    cf_template["Parameters"]["AssumeRoleArn"] = {
                        "Type": "String",
                        "Default": role_arn,
                        "Description": "ARN of role to assume"
                    }

    def _extract_provider_config(self, cf_dict: Dict) -> Dict:
        """Extract provider configuration from CloudFormation template"""
        provider_config = {}
        
        # Extract region from mappings if available
        if "Mappings" in cf_dict and "AWSRegionMap" in cf_dict["Mappings"]:
            provider_config["region"] = cf_dict["Mappings"]["AWSRegionMap"]["Region"]["Name"]
        
        # Extract assumed role if available
        if "Parameters" in cf_dict and "AssumeRoleArn" in cf_dict["Parameters"]:
            provider_config["assume_role"] = {
                "role_arn": cf_dict["Parameters"]["AssumeRoleArn"].get("Default")
            }
        
        return provider_config

    def _convert_simple_sub(self, template: str) -> str:
        """Convert simple Fn::Sub to Terraform format"""
        # Replace ${XXX} with ${var.XXX} for parameters
        return re.sub(r'\$\{([^}]+)\}', r'${var.\1}', template)

    def _convert_complex_sub(self, template: str, mapping: Dict) -> str:
        """Convert complex Fn::Sub to Terraform format"""
        result = template
        for key, value in mapping.items():
            if isinstance(value, dict):
                # Handle intrinsic functions in mapping
                value = self._convert_cf_value_to_tf(value)
            result = result.replace(f"${{{key}}}", str(value))
        return result

    def _convert_cf_value_to_tf(self, value: Any) -> Any:
        """Convert CloudFormation value to Terraform format"""
        if isinstance(value, dict):
            if len(value) == 1:
                fn_name, params = next(iter(value.items()))
                if fn_name in self.cf_to_tf_functions:
                    return self.cf_to_tf_functions[fn_name](params)
            return {k: self._convert_cf_value_to_tf(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_cf_value_to_tf(item) for item in value]
        return value

    def _convert_tf_value_to_cf(self, value: Any) -> Any:
        """Convert Terraform value to CloudFormation format"""
        if isinstance(value, str):
            # Handle string interpolation
            if "${" in value:
                for tf_func, cf_func in self.tf_to_cf_functions.items():
                    if tf_func in value:
                        return cf_func(value)
            return value
        elif isinstance(value, dict):
            return {k: self._convert_tf_value_to_cf(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_tf_value_to_cf(item) for item in value]
        return value

    def _format_dependencies(self, resource_name: str, depends_on: List[str]) -> str:
        """Format resource dependencies"""
        if not depends_on:
            return ""
        
        deps = [f'"{dep}"' for dep in depends_on]
        return f'  depends_on = [{", ".join(deps)}]\n'

    def validate_conversion(self, source: str, target: str) -> bool:
        """Validate the conversion between formats"""
        try:
            if target.lower() == "cloudformation":
                # Validate CloudFormation template
                json.loads(source) if source.startswith("{") else yaml.safe_load(source)
            else:
                # Validate Terraform HCL
                hcl2.loads(source)
            return True
        except Exception as e:
            raise ValueError(f"Validation failed: {str(e)}")
            