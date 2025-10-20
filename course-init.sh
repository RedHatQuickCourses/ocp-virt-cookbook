print_usage()
{
	echo -e """
	USAGE: $0 --type [hol|bfx] --lab [demo|role|other]
	"""
	return
}

exit_script()
{
	#cleanup
	echo -e "\nPlease replace the FIXME line in the antora.yml and antora-playbook.yml files with the title for this course. \nCommit the changes before proceeding with the course development."
	grep FIXME antora.yml antora-playbook.yml
}

handle_lab()
{
	cp -f modules/LABENV/pages/index-lab-$LAB.adoc modules/LABENV/pages/index.adoc
}

handle_type()
{
        case "$TYPE" in 
                "hol" )
                        rm -rf modules.bfx
                        ;;
                "bfx" )
                        rm -rf modules
                        mv modules.bfx modules
                        ;;
                * )
			echo -e "ERROR: you should never land here"
                        print_usage
                        exit 1
                        ;;
        esac
}

execute_init()
{
	## Get the training repository name and replace it with the placeholder string in different files
	handle_type
	handle_lab
	REPONAME=$(basename `git rev-parse --show-toplevel`)
	echo -ne "Initializing $REPONAME . . . "
	sed -i "s/REPLACEREPONAME/${REPONAME}/g" *.* > /dev/null 2>&1
	sed -i "s/REPLACEREPONAME/${REPONAME}/g" supplemental-ui/partials/header-content.hbs > /dev/null 2>&1
	echo -e "done"
	
	mv -f README-TRAINING.md README.md
}

validate_args()
{
	case "$LAB" in 
		"demo"|"role"|"other" )
			;;
		* )
			echo -e "ERROR: Invalid lab type: $LAB"
			print_usage
			exit 1
			;;
	esac
	case "$TYPE" in 
		"hol"|"bfx" )
			;;
		* )
			echo -e "ERROR: Invalid course type: $TYPE"
			print_usage
			exit 1
			;;
	esac
	execute_init
	echo -e "Initialized type to $TYPE and lab to $LAB "
	exit_script
}

cleanup()
{
	# Clean unused files for lab type
	rm -f modules/LABENV/pages/index-*.adoc
	# Clean unused files for course type
	# Remove this script
	rm -f $0
}

## Start by validating provided options and initializing variables for arguments
if [ $# -lt 4 ]
then
	echo -e "ERROR: Insufficient arguments"
	print_usage
	exit 1
fi

for arg in "$@" 
do
	case ${arg} in 
		"--lab" ) 
			shift
			LAB=$(echo $1)
			shift
			;;
		"--type" ) 
			shift
			TYPE=$(echo $1)
			shift
			;;
		"--help" )
			print_usage
			exit 0
			;;
	esac
done

validate_args


